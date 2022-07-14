
// traverse string->string dictionary tree structure, generated from python Dict by http://thot.banki.hu/ekezet/mktree8.py
const findword2 = (data,w) => {
  var cp=0; // code position in 'w'
  var p=0;  // offset in 'data'
  while(true){
//    console.log("findword",data,w,p);
    if(cp==w.length){
        // no more characters, check leaf node:
        if(data[p]!=0){
          const s=data.subarray(p+1,p+1+data[p]);
//        console.log(s);
          const decoder = new TextDecoder('UTF-8');
          return decoder.decode(s);
        }
        return "";
    }
    p+=1+data[p]; // skip len[1]+string[len]
    // dict?
    if(data[p+1]==0xFF){
        const ws=w.substring(cp);
        var st=data[p];
//        console.log("dict",p,st,ws);
        p+=2;
        const decoder = new TextDecoder('UTF-8');
        while(st>0){
            st-=1;
            s=data.subarray(p+1,p+1+data[p]); p+=1+data[p];
            if(ws==decoder.decode(s)){
                s=data.subarray(p+1,p+1+data[p]);
                return decoder.decode(s);
            }
            p+=1+data[p];
        }
        return "";
    }
    // subtree?
    const code=w.codePointAt(cp);
    while(true){
        //  xx yx yy yy yy  : xx=charcode (max 0xFFF) / yy=offset (max 256MB)
        var c=data[p]+((data[p+1]&15)<<8);
        if(c==0) return "";
        if(c==code){
            p=data[p+2]|(data[p+3]<<8)|(data[p+4]<<16)|((data[p+1]>>4)<<24);
            cp+=1; // w=w.substring(1);
            break; //return findword(data,w.substring(1),p);
        }
        p+=5;
    }
  }
}

// traverse string->int dictionary tree structure, generated from python Dict by http://thot.banki.hu/ekezet/mktree8_p.py
const findpair2 = (data,w) => {
  var cp=0; // code position in 'w'
  var p=0;  // offset in 'data'
  while(true){
//    console.log("findword",data,w,p);
    var s=data[p];
    if(s!=0){ s|=(data[p+1]<<8)|(data[p+2]<<16)|((data[p+3]>>4)<<24); p+=3; } // tricky rle coding
    // no more characters, check leaf node:
    if(cp==w.length) return s; 
    p+=1;
    // dict?
    if(data[p+1]==0xFF){
        const ws=w.substring(cp);
        var st=data[p];
//        console.log("dict",p,st,ws);
        p+=2;
        const decoder = new TextDecoder('UTF-8');
        while(st>0){
            st-=1;
            s=data.subarray(p+1,p+1+data[p]); p+=1+data[p];
            if(ws==decoder.decode(s)){
                s=data[p]|(data[p+1]<<8)|(data[p+2]<<16)|(data[p+3]<<24);
                return s;
            }
            p+=4;
        }
        return 0; // not found
    }
    // subtree?
    const code=w.codePointAt(cp);
    while(true){
        //  xx yx yy yy yy  : xx=charcode (max 0xFFF) / yy=offset (max 256MB)
        var c=data[p]+((data[p+1]&15)<<8);
        if(c==0) return 0;
        if(c==code){
            p=data[p+2]|(data[p+3]<<8)|(data[p+4]<<16)|((data[p+1]>>4)<<24);
            cp+=1; // w=w.substring(1);
            break; //return findword(data,w.substring(1),p);
        }
        p+=5;
    }
  }
}



var wordmap_ok=0;
var wordmap=0;
var wordpairs_ok=0;
var wordpairs=0;

// split input string to words and lookup in the dictionary (check pairs frequency when there are multiple choices)
const ekezet1 = (txt) => {

    var lastw="NoNe";
    var w="";
    var out="";
    for(c of txt+" "){
//        console.log(c);
        if( (c>='0' && c<='9') || (c>='a' && c<='z') || (c>='A' && c<='Z') || (c.codePointAt(0)>=192 && c.codePointAt(0)<688) ){
            w+=c;
            continue;
        }
//        console.log(c,c.codePointAt(0));
        if(w){
//            console.log(w);
            l=w.toLowerCase();
            uj=findword2(wordmap, l);
//            console.log(w,l,uj);
            if(uj!=""){
                us=uj.split('|');
//                console.log(us.length);
                if(us.length==2 && wordpairs_ok!=0){
                    c1=findpair2(wordpairs, lastw+"+"+us[0]);
                    c2=findpair2(wordpairs, lastw+"+"+us[1]);
//                    console.log(c1,c2);
                    if(c1>c2*5) uj=us[0]; else
                    if(c2>c1*5) uj=us[1]; else
                    if(c2>c1) uj=us[1]+"|"+us[0];
                    console.log(lastw,l,us,c1,c2,uj);
                } 
//                else console.log(l,uj);
                lastw=uj.toLowerCase();
                out+=uj;
            } else {
                lastw=l;
                out+=w;
//                console.log(l,"???");
            }
            w="";
        }
        out+=c;
    }
    alert(out);
    navigator.clipboard.writeText(out);
}

const ekezet2 = (txt) => {
    if(wordmap_ok>0){
        // DB already loaded
        ekezet1(txt);
        return;
    }

    // load dictionary database on-demand:
    const start = Date.now();

    fetch( browser.runtime.getURL("wordpairs.dat") )
        .then( response => response.arrayBuffer() )
        .then( function(array){
//                console.log(array);
                wordpairs=new Uint8Array(array);
                wordpairs_ok=1;
                console.log("wordpair load time:",Date.now() - start);

//                console.log(findpair2(wordpairs,"meg+kellett"));
//                console.log(findpair2(wordpairs,"kellett+meg"));
//                console.log(findpair2(wordpairs,"enni+meg"));
//                console.log(findpair2(wordpairs,"egy+lehet"));
//                console.log(findpair2(wordpairs,"nincs+masik"));
        } );


    fetch( browser.runtime.getURL("wordmap.dat") )
        .then( response => response.arrayBuffer() )
        .then( function(array){
//                console.log(array);
                wordmap=new Uint8Array(array);
                wordmap_ok=1;
                console.log("wordmap load time:",Date.now() - start);

//                console.log(findword2(wordmap,"elek"));
//                console.log(findword2(wordmap,"eles"));
//                console.log(findword2(wordmap,"ho"));
//                console.log(findword2(wordmap,"hu"));
//                console.log(findword2(wordmap,"ha"));
//                console.log(findword2(wordmap,"evekbeliek"));
//                console.log(findword2(wordmap,"evekbeliekezik"));

                ekezet1(txt);
        } );

}

// register event handlers (hotkey & context menu)

const handle = (message) => {
    console.log(message);
    ekezet2(message.ekezetesit);
}

browser.runtime.onMessage.addListener(handle);

document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key == "L") {
        navigator.clipboard.readText().then( clipText => ekezet2(clipText) );
    }
}, false);



const hunaccent={
    'a': "aá",
    'e': "eé",
    'i': "ií",
    'o': "oóöő",
    'u': "uúüű"
}

// differential string decoding for hungarian charset: only stores accented charmap differences in 1/2 bits (data), and reproduce it using the original string (w):
const huncode = (w,data) => {
    var out="";
    var bits=0;
    var c;
    for(c of w){
        if(c in hunaccent){
            const h=hunaccent[c];
//            console.log(h);
            if(h.length==2){
                out+=h[(data>>bits)&1]; // 1-bit char selector
                bits+=1;
            } else {
                out+=h[(data>>bits)&3]; // 2-bit char selector
                bits+=2;
            }
        } else out+=c;
    }
//    console.log("huncode",w,data,bits,out);
    return out; // "HUN:"+w;
}

// traverse ascii string->string dictionary tree structure, generated from python Dict by http://thot.banki.hu/ekezet/mktree9hun.py  (use_rle=8, use_huncode=13)
const findword2 = (data,w) => {
  var cp=0; // code position in 'w'
  var p=0;  // offset in 'data'
  var end=data.length;
//  console.log(size);
  while(true){
//    console.log("findword",w,cp,p,end-p,data[p]);
    const flag=data[p]; // d0llllll+char[l] for utf8 (d=dict_flag, l=len) / d1exxxxx(+xxxxxxxx) for huncode (d=dict_flag, e=more_bits_flag, x=5/13 bits of binary data)
    if(cp==w.length){
        // no more characters, check leaf node:
        if(flag&64){
          // huncoded string
          if(flag&32) return huncode(w, (flag&31)|(data[p+1]<<5) ); // 13 bit
          return huncode(w, (flag&31) ); // 5 bit
        }
        if(flag&63){
          // UTF8-encoded string
          const s=data.subarray(p+1,p+1+(flag&63));
          const decoder = new TextDecoder('UTF-8');
          return decoder.decode(s);
        }
        return "";
    }
    if(flag&64) p+=(flag&32)?2:1; else p+=1+(flag&63); // skip huncode/utf8 string

    // dict?
    if(flag&128){
        const ws=w.substring(cp);
//        console.log("dict",p,end-p,ws);
        const decoder = new TextDecoder('UTF-8');
        while(p<end){
            s=data.subarray(p+1,p+1+data[p]); p+=1+data[p]; // read utf8 string (key)
            if(ws==decoder.decode(s)){
                if(data[p]&64){
                    // huncoded string!
                    if(data[p]&128) w=w+"|"+w;
                    if(data[p]&32) return huncode(w, (data[p]&31)|(data[p+1]<<5) ); // 13 bit
                    return huncode(w, (data[p]&31) ); // 5 bit
                }
                // utf8-encoded string
                s=data.subarray(p+1,p+1+data[p]);
                return decoder.decode(s);
            }
            if(data[p]&64) p+=(data[p]&32)?2:1; else p+=1+data[p]; // skip huncode/utf8 string
        }
        return ""; // not found
    }

    // subtree?
    const code=w.codePointAt(cp);
    if(code>255) return ""; // non-ascii key not supported here!
    while(true){
        if(p>=end) return ""; // not found
        // read charcode (c), s-len (sl), length (l)
//        var c=data[p]+((data[p+1]&15)<<8);
//        var sl=data[p+1]>>4;
        var c=data[p];   // char code
        var l=data[p+1]; // rle code
        p+=2;
        // RLE-coded block length:
        // l=0-252 -> 0-252
        // l=253   -> 253 + read 8 bit number
        // l=254   -> read 16 bit number
        // l=255   -> read 24 bit number
        if(l>=253){
            const sl=l-252; // 1-3
            if(sl==1) l=253+data[p]; // 1 byte length code
            else if(sl==2) l=data[p]|(data[p+1]<<8); // 2 byte length code
            else if(sl==3) l=data[p]|(data[p+1]<<8)|(data[p+2]<<16); // 3 byte length code
            p+=sl;
        }
        if(c==code){
            end=p+l;
            cp+=1; // w=w.substring(1);
            break; //return findword(data,w.substring(1),p);
        }
        p+=l; // skip this subtree!
    }
  }
}


// traverse unicode string->int dictionary tree structure, generated from python Dict by http://thot.banki.hu/ekezet/mktree9pair.py  (use_rle=7)
const findpair2 = (data,w) => {
  var cp=0; // code position in 'w'
  var p=0;  // offset in 'data'
  var end=data.length;
//  console.log(size);
  while(true){
//    console.log("findword",w,cp,p,end-p,data[p]);
    const flag=data[p]; // dexxxxxx  (d=dict_flag, e=more_bits, xxxxxx=6 bits of value)
    p+=1;

    // decode VALUE  6+7+8 bits
    var value=flag&63; // first 6 bits
    if(flag&64){ // more_bits set?
        value|=((data[p]&127)<<6);         // additional 7 bits (total 6+7=13)
        if(data[p]&128){ // 3 bytes?
            p+=1; value|=(data[p]<<(6+7)); value+=64*128;       // additional 8 bits (total 6+7+8=21)
        } else value+=64;
        p+=1;
    }
    if(cp==w.length) return value;

    // dict?
    if(flag&128){
        const ws=w.substring(cp);
//        console.log("dict",p,end-p,ws);
        const decoder = new TextDecoder('UTF-8');
        while(p<end){
            s=data.subarray(p+1,p+1+data[p]); p+=1+data[p]; // read utf8 string (key)

            // decode VALUE  7+7+8 bits
            value=data[p]&127; // first 7 bits
            if(data[p]&128){   // more_bits set?
                p+=1;
                value|=((data[p]&127)<<7);         // additional 7 bits (total 7+7=14)
                if(data[p]&128){ // 3 bytes?
                    p+=1; value|=(data[p]<<(7+7)); value+=128*128;       // additional 8 bits (total 7+7+8=22)
                } else value+=128;
            }
            p+=1;
            if(ws==decoder.decode(s)) return value;
        }
        return 0; // not found
    }

    // subtree?
    const code=w.codePointAt(cp);
    if(code>=512) return 0; // non-latin charcode key not supported here!
    while(true){
        if(p>=end) return 0; // not found
        var c=data[p]|((data[p+1]&1)<<8);   // char code (9 bits)
        var l=data[p+1]>>1;                 // rle code  (7 bits)
        p+=2;
        // RLE-coded block length:
        // l=0-124 -> 0-124
        // l=125   -> 125 + read 8 bit number
        // l=126   -> read 16 bit number
        // l=127   -> read 24 bit number
        if(l>=125){
            const sl=l-124; // 1-3
            if(sl==1) l=125+data[p]; // 1 byte length code
            else if(sl==2) l=data[p]|(data[p+1]<<8); // 2 byte length code
            else if(sl==3) l=data[p]|(data[p+1]<<8)|(data[p+2]<<16); // 3 byte length code
            p+=sl;
        }
        if(c==code){
            end=p+l;
            cp+=1; // w=w.substring(1);
            break; //return findword(data,w.substring(1),p);
        }
        p+=l; // skip this subtree!
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


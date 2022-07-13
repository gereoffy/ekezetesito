
var wordmap_ok=0;
var wordmap = {};
var wordpairs = {};

const ekezet1 = (txt) => {

    lastw="NoNe";
    w="";
    out="";
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
            if(l in wordmap){
                uj=wordmap[l];
                us=uj.split('|');
//                console.log(us.length);
                if(us.length==2){
                    k=lastw+"+"+us[0];
                    if(k in wordpairs) c1=wordpairs[k]; else c1=2;
                    k=lastw+"+"+us[1];
                    if(k in wordpairs) c2=wordpairs[k]; else c2=1;
//                    console.log(c1);
//                    console.log(c2);
                    if(c1>c2*5) uj=us[0]; else
                    if(c2>c1*5) uj=us[1]; else
                    if(c2>c1) uj=us[1]+"|"+us[0];
                    console.log(lastw,l,us,c1,c2,uj);
                } else
                    console.log(l,uj);
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
        // DB already 
        ekezet1(txt);
        return;
    }
    const start = Date.now();
    // load database:
    fetch( browser.runtime.getURL("wordpairs.dat") ).then( function(response) {
        console.log("wordpairs.json",response.statusText);
        response.json().then( function(jsondata){
            wordpairs=jsondata;
            console.log("wordpairs load time:",Date.now() - start);
        } );
    } );
    fetch( browser.runtime.getURL("wordmap.dat") ).then( function(response) {
        console.log("wordmap.json",response.statusText);
        response.json().then( function(jsondata){
            wordmap=jsondata;
            wordmap_ok=1;
            console.log("wordmap load time:",Date.now() - start);
            ekezet1(txt);
        } );
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


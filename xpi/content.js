
//const buildKey = (text) => {
//    const key = window.location.toString() + text;
//    return key
//}


const ekezet2 = (txt) => {
//    for(w of txt.split(/\s+/) ){
//	if(w in wordmap) console.log(wordmap[w]);
//    }
    lastw="NoNe";
    w="";
    out="";
    for(c of txt+" "){
//        console.log(c);
        if( (c>='0' && c<='9') || (c>='a' && c<='z') || (c>='A' && c<='Z') ){
            w+=c;
            continue;
        }
        if(w){
//            console.log(w);
            uj=w;
            l=w.toLowerCase();
            //
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
            }
            lastw=uj;
            out+=uj;
            w="";
        }
        out+=c;
    }
    alert(out);
    navigator.clipboard.writeText(out);
}

const ekezet = (txt) => {

    console.log(txt);

    fetch('https://arp.interoot.hu/list/ekezet.cgi',
	{   method: 'POST',
	    cache: 'no-cache',
	    headers: {'Content-Type': 'application/json'},
	    body: txt
	} ).then(function(response) {
        console.log(response.ok);
        console.log(response.statusText);
        if (!response.ok) { throw Error(response.statusText); }

        response.text().then( function(txt2) {
            alert(txt2);
            navigator.clipboard.writeText(txt2);
        } );
    }).catch(function(error) {
            console.log('EXCEPTION: '+error);
    });

}


const highlightSelection = (e) => {

//    sel= window.getSelection ? window.getSelection() : (document.getSelection ? document.getSelection() : (document.selection ? document.selection.createRange().text : ''));
//    alert(sel);

//    alert(navigator.clipboard.readText());

    navigator.clipboard.readText().then(  clipText => ekezet(clipText)   );

    
//    console.log(e);
    
//    var selection = new window.getSelection,
//    const selection = document.getSelection();
//    var selectedText = selection.toString();

//    var selectedText = selection.anchorNode.data;
//    alert(selectedText);

//    var textarea = window.document.querySelector('textarea');
//    var textarea = document.getElementById('edit-comment-body-0-value');
    
//    alert(textarea.value);
//    alert(textarea.selection);
//    console.log(textarea);
//    console.log(textarea.selectionStart);
//    console.log(textarea.selectionEnd);
//    console.log(textarea.selection);

//    textarea.value = textarea.value.replace(selectedText, "HelloWorld");
//    textarea.value = "HelloWorld";
//    textarea.innerHTML = "HelloWorld";
//    textarea.innerText = "HelloWorld";

//    const sel = document.getSelection();
//    console.log(sel);

//    const sel = window.getSelection();
//    const sel = document.activeElement.value;
//    const range = sel.getRangeAt(0);

//    range = (document.all) ? document.selection.createRange().text : document.getSelection();

//    console.log(range);
//    alert(range);
    
//    sel.deleteFromDocument();
//    sel.modify("Helloka");
//    const wrapper = document.createElement("span");
//    wrapper.style.backgroundColor = "#EEEE00";
//    wrapper.style.color = "#111111";
//    wrapper.classList.add("matt-highlight");
//    wrapper.style.fontSize = "1.2em";
//    range.surroundContents(wrapper);
}

//const handle = (message) => {
//    if (message == "highlight") {
//        highlightSelection(message);
//    }
//}

const handle = (message) => {
    console.log(message);
//    ekezet(message.ekezetesit);
    ekezet2(message.ekezetesit);
//    alert(wordmap["meg"]);

//    console.log(obj);
//    if (message == "highlight") {
//        highlightSelection(obj);
//    }
}

browser.runtime.onMessage.addListener(handle);

document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key == "L") {
        highlightSelection(event);
    }
}, false);

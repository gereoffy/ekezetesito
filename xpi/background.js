const onCreated = () => null

browser.contextMenus.create({
  id: "highlight-selection",
  title: "ekezetesit: %s",
  contexts: ["selection"]
}, onCreated);

browser.contextMenus.onClicked.addListener(function(info, tab) {
    switch (info.menuItemId) {
    case "highlight-selection":
        browser.tabs.sendMessage(tab.id, {ekezetesit: info.selectionText});
        break;
    }
});

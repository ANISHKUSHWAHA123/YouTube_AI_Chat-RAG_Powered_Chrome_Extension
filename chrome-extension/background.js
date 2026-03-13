let currentVideoId = null;

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({
    openPanelOnActionClick: true
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  if (message.type === "VIDEO_ID") {
    currentVideoId = message.videoId;
  }

  if (message.type === "GET_VIDEO_ID") {
    sendResponse({ videoId: currentVideoId });
  }

  return true;
});
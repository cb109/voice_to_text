importScripts(
  'https://storage.googleapis.com/workbox-cdn/releases/6.5.4/workbox-sw.js'
);

workbox.core.skipWaiting();
workbox.core.clientsClaim();

workbox.precaching.precacheAndRoute(self.__WB_MANIFEST || []);

let messageChannelPort;
self.addEventListener('message', event => {

  if (event.data && event.data.type === 'INIT_PORT') {
    messageChannelPort = event.ports[0];
  }

  if (messageChannelPort && event.data && event.data.type === 'PING') {
    messageChannelPort.postMessage({payload: 'PONG'});
  }
});

const shareTargetHandler = async ({event}) => {
  if (messageChannelPort) {
    messageChannelPort.postMessage({payload: 'BUSY'});
  }

  return event.respondWith(null);
};

workbox.routing.registerRoute('/_share-target', shareTargetHandler, 'POST');

console.log('service worker initialized');

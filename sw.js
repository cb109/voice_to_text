importScripts(
  'https://storage.googleapis.com/workbox-cdn/releases/6.5.4/workbox-sw.js'
);

workbox.core.skipWaiting();
workbox.core.clientsClaim();

workbox.precaching.precacheAndRoute(self.__WB_MANIFEST || []);

const shareTargetHandler = async ({event}) => {
  console.log('event', event);
  // alert(event);

  // const formData = await event.request.formData();
  // console.log('formData', formData);
  // alert(formData);

  return Response.redirect('/share/', 303);
};

workbox.routing.registerRoute(
  '/_share-target',
  shareTargetHandler,
  'POST'
);

console.log('service worker initialized');

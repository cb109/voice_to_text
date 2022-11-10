importScripts(
    'https://storage.googleapis.com/workbox-cdn/releases/6.5.4/workbox-sw.js'
);

workbox.core.skipWaiting();
workbox.core.clientsClaim();

workbox.precaching.precacheAndRoute(self.__WB_MANIFEST || []);

const shareTargetHandler = async ({event}) => {
  // if (broadcastChannel) {
  //   broadcastChannel.postMessage('Saving media locally...');
  // }

  console.log('event', event);

  const formData = await event.request.formData();
  console.log('formData', formData);
  // const audioFiles = formData.getAll('audio');
  // console.log('audioFiles', audioFiles);
  // alert('shared ' + audioFiles.length + ' audio files');
  // const cache = await caches.open(cacheName);

  // for (const mediaFile of mediaFiles) {
  //   // TODO: Instead of bailing, come up with a
  //   // default name for each possible MIME type.
  //   if (!mediaFile.name) {
  //     if (broadcastChannel) {
  //       broadcastChannel.postMessage('Sorry! No name found on incoming media.');
  //     }
  //     continue;
  //   }

  //   const cacheKey = new URL(`${urlPrefix}${Date.now()}-${mediaFile.name}`, self.location).href;
  //   await cache.put(
  //     cacheKey,
  //     new Response(mediaFile, {
  //       headers: {
  //         'content-length': mediaFile.size,
  //         'content-type': mediaFile.type,
  //       },
  //     })
  //   );
  // }

  // // Use the MIME type of the first file shared to determine where we redirect.
  // const routeToRedirectTo = [
  //   audioRoute,
  //   imagesRoute,
  //   videosRoute,
  // ].find((route) => mediaFiles[0].type.startsWith(route.mimePrefix));

  // const redirectionUrl = routeToRedirectTo ? `/#${routeToRedirectTo.href}` : '/';

  // // After the POST succeeds, redirect to the main page.
  // return Response.redirect(redirectionUrl, 303);
};

workbox.routing.registerRoute(
  '/_share-target',
  shareTargetHandler,
  'GET'
);

console.log('service worker initialized');

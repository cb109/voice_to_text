# voice-to-text

![](voice_to_text/core/static/icons/icon_192.png)

A web app that you can install on your phone from Chrome (only Chrome right now has the needed APIs), which allows
to share an audio file (e.g. voice messages) to it to transcribe the audio
into text (using [https://replicate.com/openai/whisper](https://replicate.com/openai/whisper), you need an account!).

## How it works

It simply passes the shared audio file to [openai/whisper](https://github.com/openai/whisper), which produces pretty good results in  reasonable time. You could host/run it yourself, but need a somewhat beefy server (at least regarding memory), so I chose to use a hosted service instead, since this is merely a prototype right now.

> **Warning**: This means the audio is uploaded to the replicate.com servers and stored there along with the transcription.

## How to use

- Register at [https://replicate.com/](https://replicate.com/), you can use it a while for free, but at some point they will charge you and you'll have to add credit card information.
- Host the Django web app on your server, make sure the `manifest.json` is served from the root of your domain.
- Open the web app URL in your phone's Chrome browser.
- In the page options (...), select "Install App". This will register it as a target for "Share" actions.
- Share any audio file in other apps (e.g. your chat program like WhatsApp, Telegram, Signal, ...) and select the web app as the share target.
- The web app should open and show the transcribed text after a while (your API calls can be inspected on your replicate.com > Predictions page).

### Icon based on
<a href="https://www.flaticon.com/free-icons/voice" title="voice icons">Voice Icons on Freepik - Flaticon</a>

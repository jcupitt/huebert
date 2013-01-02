=======
huebert
=======

This program will attempt to play music and pulse a set of Philips Hue
lightblubs in time.

At the moment, it's unfinished. Here's what it does right now:

* play an audio stream using the gstreamer Python bindings

* take a tap from the audio stream just before a 1s queue to create a side
  stream of audio data from one second before the playback point
 
* run that uncompressed audio stream through some simple signal processing
  coded in C to calculate various parameters 

* generate a set of light change commands from the audio parameters

* send those command to the Hue bridge using the Requests library

Here's what's missing:

* the signal processing is just a placeholder, all it does right now is
  calculate RMS

* there's nothing to synchronise the light commands to the music, so currently
  you see light changes about a second ahead of the music 

Here's the plan:

* use fftw3 to spot frequency bands

* analyse a 0.1s window 1s ahead, a 1s ahead window, and a 1s head 9s behind
  window, and combine that with RMS 

* use the GstBuffer timestamps to timestamp planned lighting changes

* have a separate optimiser to allocate the 20 light changes we get a second
  across the light changes requested by the sound-to-light processing

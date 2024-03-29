'use client'
//import Image from "next/image";
//import { Button } from "@/app/components/Button";
import {useState, useEffect} from "react";


export default function Home() {
  function jpeg_binary_to_base64(buffer){
    var base64 = btoa(new Uint8Array(buffer).reduce(function (data, byte) {
        return data + String.fromCharCode(byte);
    }, ''));
    return "data:image/jpeg;base64," + base64;
  }

  const [recording, setRecording] = useState(false);
  const [recording_video, setRecordingVideo] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('/api/py/recording', {
        method: 'GET',
      }).then((res) => {
        res.json().then((data) => {
          setRecording(data.recording);
        });
      });
      console.log("Checking recording status");
    }, 10000);

    var ws = undefined

    //console.log(window.location.host);
   
     ws = new WebSocket("ws://ubuntu:8000/ws");
    
     ws.onopen = function () {
   
       console.log("Connected.");
   };
   
   ws.onclose = function () {
       console.log("Disconnected.");
   };
   
   ws.onmessage = function (event) {
       var camera_image = document.getElementById("camera_image");
       var reader = new FileReader();
       reader.readAsDataURL(event.data);
       reader.onloadend = function () {
           camera_image.src = reader.result;
       }
   }
  }, []);

  function record() {
    setRecording(true);
    fetch('/api/py/record', {
      method: 'POST',
    });  
  }

  function record_video() {
    if (recording_video) {
      setRecordingVideo(false);
      fetch('/api/py/stop-video', {
        method: 'POST',
      });
    } else {
      setRecordingVideo(true);
      fetch('h/api/py/record-video', {
        method: 'POST',
      });
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-2xl">Bicycle Recording App</h1>
      <div>
      <img id="camera_image" src="" alt="Camera Image"/>
      </div>
      <div className="container mx-auto px-4">
        <div class="flex justify-center space-x-4">
          <button className="px-12 py-7 text-xl bg-slate-800 text-slate-50 rounded-full" onClick={record} disabled={recording}>{recording? 'Recording' : 'Record 30 seconds with Sensor'}</button>
          <button className="px-12 py-7 text-xl bg-slate-800 text-slate-50 rounded-full" onClick={record_video}>{recording_video? 'Stop Recording' : 'Record Video'}</button>
        </div>
      </div>
      <p>This application will allow you to record your cycling trips with <a href="https://www.rerun.io/">rerun</a> for later analysis.</p>
    </main>
  );
}

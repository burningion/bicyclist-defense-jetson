'use client'
import Image from "next/image";
import { Button } from "@/app/components/Button";
import {useState, useEffect} from "react";


export default function Home() {
  function jpeg_binary_to_base64(buffer){
    var base64 = btoa(new Uint8Array(buffer).reduce(function (data, byte) {
        return data + String.fromCharCode(byte);
    }, ''));
    return "data:image/jpeg;base64," + base64;
  }

  var ws = undefined

  console.log(location.host);

  ws = new WebSocket("ws://" + location.host + "/ws");

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
        console.log("Received message.");
        camera_image.src = reader.result;
    }
}

  const [recording, setRecording] = useState(false);
  useEffect(() => {
    const interval = setInterval(() => {
      fetch('/api/py/recording', {
        method: 'GET',
      }).then((res) => {
        res.json().then((data) => {
          setRecording(data.recording);
        });
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  function record() {
    setRecording(true);
    fetch('/api/py/record', {
      method: 'POST',
    });
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-9xl">Bicycle Recording App</h1>
      <img id="camera_image" src="" alt="Camera Image"/>
      <p>This application will allow you to record your cycling trips with <a href="https://www.rerun.io/">rerun</a> for later analysis.</p>
      
      <Button className="px-12 py-7 text-9xl" onClick={record} disabled={recording}>{recording? 'Recording' : 'Record 30 seconds'}</Button>
    </main>
  );
}

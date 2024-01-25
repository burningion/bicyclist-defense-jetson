'use client'
import Image from "next/image";
import { Button } from "@/app/components/Button";
import {useState, useEffect} from "react";


export default function Home() {
  
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
      <Button className="px-12 py-7 text-9xl" onClick={record} disabled={recording}>{recording? 'Recording' : 'Record 30 seconds'}</Button>
    </main>
  );
}

'use client'
import Image from "next/image";
import { Button } from "@/app/components/Button";

function record() {
  fetch('/api/py/record', {
    method: 'POST',
  });
}

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Button className="px-12 py-7 text-9xl" onClick={record}>Click me</Button>
    </main>
  );
}

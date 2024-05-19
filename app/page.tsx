"use client";

import { useQRCode } from "next-qrcode";
import React, { useState, useEffect } from "react";
import useOrigin from "@/hooks/use-origin";
import makeId from "@/lib/makeId";

export default function Home() {
  const currentDomain = useOrigin();
  const { SVG: QRCode } = useQRCode();
  const [codeURL, setCodeURL] = useState("https://hack.club");
  const [room, setRoom] = useState(makeId(12));

  useEffect(() => {
    if (currentDomain) {
      setCodeURL(`${currentDomain}/room/${room}/${makeId(6)}`);
    }
  }, [currentDomain, room]);

  const handleNewPlayer = () => {
    setCodeURL(`${currentDomain}/room/${room}/${makeId(6)}`);
  };

  return (
    <div className="grid h-screen place-items-center">
      <a href={codeURL} target="_blank" className="text-blue-500 underline">
        {codeURL}
      </a>
      <div>
        {currentDomain && (
          <div className="rounded-xl w-min h-min block overflow-hidden">
            <QRCode
              text={codeURL}
              options={{ errorCorrectionLevel: "Q", width: 200 }}
            ></QRCode>
          </div>
        )}
      </div>
      <button onClick={handleNewPlayer}>New player!</button>
      <h1 className="text-xl text-red-400 text-center">
        SCAN TO PLAY<br></br>BRING A FRIEND
      </h1>
    </div>
  );
}

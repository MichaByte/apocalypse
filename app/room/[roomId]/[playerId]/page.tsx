"use client";
import { Socket, io } from "socket.io-client";
import { useState, useEffect } from "react";

export default function Room({
  params,
}: {
  params: { roomId: string; playerId: string };
}) {
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<Socket | null>(null);

  console.log(params.playerId);
  useEffect(() => {
    const newSocket = io(`http://10.93.93.222:8000/`);
    setSocket(newSocket);
    newSocket.on("new_message", (msg: string) => {
      setMessages((prevMessages) => [...prevMessages, msg]);
    });
    newSocket.on("connect", () => {
      newSocket.emit("create_room", params.roomId);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected");
    });

    newSocket.on("connect_error", (err) => {
      console.error(`connect_error due to ${err}`);
    });

    return () => {
      newSocket.disconnect();
    };
  }, [params.roomId]);

  function sendText() {
    const msg = (document.getElementById("message-box") as HTMLInputElement)
      .value;
    socket!.emit("user_message", `The user ${params.playerId} says: ${msg}`);
    setMessages((prevMessages) => {
      console.log(prevMessages);
      console.log(msg);
      return [...prevMessages, msg];
    });
    (document.getElementById("message-box") as HTMLInputElement).value = "";
  }
  return (
    <>
      <p suppressHydrationWarning={true}>
        You are {params.playerId}. Send a message to start, and try to get the
        AI to let you in instead of the other player(s)!
      </p>
      <div className="bg-slate-100 text-black w-screen h-screen overflow-scroll">
        <div>
          {messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}
        </div>
        <input
          type="text"
          id="message-box"
          className="bg-slate-600 text-white w-84"
          onSubmit={sendText}
        ></input>
        <button className="bg-slate-600 text-white" onClick={sendText}>
          Send!
        </button>
      </div>
    </>
  );
}

// App.jsx
import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";
import ChatBot from "./components/ChatBot";
import { useState } from "react";

function App() {
  const [scriptName, setScriptName] = useState(null);

  return (
    <>
      <Canvas shadows camera={{ position: [0, 0, 8], fov: 42 }}>
        <color attach="background" args={["#ececec"]} />
        <Experience playAudio={{ script: scriptName }} />
      </Canvas>

      <ChatBot onBotReply={setScriptName} />
    </>
  );
}

export default App;
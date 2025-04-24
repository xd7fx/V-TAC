import { useGLTF, useFBX, useAnimations } from "@react-three/drei";
import { useRef, useEffect, useState } from "react";

const animationMap = {
  welcome: "Standing Greeting",
  pizzas: "Angry Gesture",
};

const visemeMap = {
  A: "viseme_PP",
  B: "viseme_kk",
  C: "viseme_I",
  D: "viseme_aa",
  E: "viseme_E",
  F: "viseme_U",
  G: "viseme_FF",
  H: "viseme_TH",
  X: "viseme_sil",
};

export function Avatar({ playAudio, script = "current", ...props }) {
  const [mouthCues, setMouthCues] = useState([]);
  const intervalRef = useRef(null);
  const audioRef = useRef(null);

  const { nodes, materials } = useGLTF("/models/646d9dcdc8a5f5bddbfac913.glb");
  const { animations: idleAnim } = useFBX("/animations/Idle.fbx");
  const { animations: angryAnim } = useFBX("/animations/Angry Gesture.fbx");
  const { animations: greetAnim } = useFBX("/animations/Standing Greeting.fbx");

  idleAnim[0].name = "Idle";
  angryAnim[0].name = "Angry Gesture";
  greetAnim[0].name = "Standing Greeting";

  const group = useRef();
  const { actions } = useAnimations([idleAnim[0], angryAnim[0], greetAnim[0]], group);

  useEffect(() => {
    console.log("✅ Avatar component mounted");
    actions.Idle?.reset().fadeIn(0.5).play();
  }, []);

  useEffect(() => {
    if (!playAudio) {
      console.warn("⛔ playAudio is false or missing");
      return;
    }

    if (intervalRef.current) clearInterval(intervalRef.current);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }

    const audio = new Audio(`http://localhost:5000/temp/${script}.wav`);
    audioRef.current = audio;

    fetch(`http://localhost:5000/temp/${script}.json`)
      .then((res) => {
        if (!res.ok) throw new Error("❌ Lipsync file not found");
        return res.json();
      })
      .then((data) => {
        const cues = data.mouthCues || [];
        setMouthCues(cues);

        if (audio.readyState >= 2) {
          audio.play().catch(console.warn);
        } else {
          audio.oncanplaythrough = () => audio.play().catch(console.warn);
        }

        const animKey = animationMap[script];
        if (animKey && actions[animKey]) {
          actions[animKey].reset().fadeIn(0.5).play();
        }

        console.log("🎭 Available visemes:", Object.keys(nodes?.Wolf3D_Head?.morphTargetDictionary || {}));

        let lastIndex = null;

        intervalRef.current = setInterval(() => {
          const currentTime = audio.currentTime;
          const cue = cues.find(c => currentTime >= c.start && currentTime <= c.end);

          if (cue) {
            const viseme = visemeMap[cue.value];
            const index = nodes?.Wolf3D_Head?.morphTargetDictionary?.[viseme];

            if (index !== undefined && index !== lastIndex) {
              if (lastIndex !== null) {
                nodes.Wolf3D_Head.morphTargetInfluences[lastIndex] = 0;
                nodes.Wolf3D_Teeth.morphTargetInfluences[lastIndex] = 0;
              }

              nodes.Wolf3D_Head.morphTargetInfluences[index] = 1;
              nodes.Wolf3D_Teeth.morphTargetInfluences[index] = 1;

              lastIndex = index;
            }
          } else if (lastIndex !== null) {
            nodes.Wolf3D_Head.morphTargetInfluences[lastIndex] = 0;
            nodes.Wolf3D_Teeth.morphTargetInfluences[lastIndex] = 0;
            lastIndex = null;
          }
        }, 50);

        audio.onended = () => {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          actions.Idle?.reset().fadeIn(0.5).play();
        };
      })
      .catch((e) => {
        console.error("❌ Failed to load lipsync or audio:", e);
      });

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current = null;
      }
    };
  }, [playAudio, script]);

  return (
    <group ref={group} {...props} dispose={null}>
      <primitive object={nodes.Hips} />
      <skinnedMesh geometry={nodes.Wolf3D_Body.geometry} material={materials.Wolf3D_Body} skeleton={nodes.Wolf3D_Body.skeleton} />
      <skinnedMesh geometry={nodes.Wolf3D_Outfit_Bottom.geometry} material={materials.Wolf3D_Outfit_Bottom} skeleton={nodes.Wolf3D_Outfit_Bottom.skeleton} />
      <skinnedMesh geometry={nodes.Wolf3D_Outfit_Footwear.geometry} material={materials.Wolf3D_Outfit_Footwear} skeleton={nodes.Wolf3D_Outfit_Footwear.skeleton} />
      <skinnedMesh geometry={nodes.Wolf3D_Outfit_Top.geometry} material={materials.Wolf3D_Outfit_Top} skeleton={nodes.Wolf3D_Outfit_Top.skeleton} />
      <skinnedMesh geometry={nodes.Wolf3D_Hair.geometry} material={materials.Wolf3D_Hair} skeleton={nodes.Wolf3D_Hair.skeleton} />
      <skinnedMesh geometry={nodes.EyeLeft.geometry} material={materials.Wolf3D_Eye} skeleton={nodes.EyeLeft.skeleton} morphTargetDictionary={nodes.EyeLeft.morphTargetDictionary} morphTargetInfluences={nodes.EyeLeft.morphTargetInfluences} />
      <skinnedMesh geometry={nodes.EyeRight.geometry} material={materials.Wolf3D_Eye} skeleton={nodes.EyeRight.skeleton} morphTargetDictionary={nodes.EyeRight.morphTargetDictionary} morphTargetInfluences={nodes.EyeRight.morphTargetInfluences} />
      <skinnedMesh geometry={nodes.Wolf3D_Head.geometry} material={materials.Wolf3D_Skin} skeleton={nodes.Wolf3D_Head.skeleton} morphTargetDictionary={nodes.Wolf3D_Head.morphTargetDictionary} morphTargetInfluences={nodes.Wolf3D_Head.morphTargetInfluences} />
      <skinnedMesh geometry={nodes.Wolf3D_Teeth.geometry} material={materials.Wolf3D_Teeth} skeleton={nodes.Wolf3D_Teeth.skeleton} morphTargetDictionary={nodes.Wolf3D_Teeth.morphTargetDictionary} morphTargetInfluences={nodes.Wolf3D_Teeth.morphTargetInfluences} />
    </group>
  );
}

useGLTF.preload("/models/646d9dcdc8a5f5bddbfac913.glb");

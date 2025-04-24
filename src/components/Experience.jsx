import { Environment, useTexture } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import { Avatar } from "./Avatar";

export const Experience = ({ playAudio, script }) => {
  const texture = useTexture("textures/vtac_stadium.jpg");
  const viewport = useThree((state) => state.viewport);

  return (
    <>
      <Avatar
        position={[0, -3, 3.5]}
        scale={2.5}
        rotation={[-0.6, 0, 0]}
        playAudio={playAudio}
        script={script}
      />

      <Environment preset="sunset" />
      <mesh position={[0, 0.2, 0.5]}>
        <planeGeometry args={[viewport.width, viewport.height]} />
        <meshBasicMaterial map={texture} />
      </mesh>
    </>
  );
};

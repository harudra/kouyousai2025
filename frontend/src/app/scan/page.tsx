"use client";

import { Box, Text, Flex, Button } from "@chakra-ui/react";
import jsQR from "jsqr";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { upsertVisited, readVisitor } from "./api";

export default function Page() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [result, setResult] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("QRコードをかざしてください");
  const [completed, setCompleted] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleReturnHome = () => {
    setCompleted(false);
    router.push("/");
  };

  useEffect(() => {
    const constraints: MediaStreamConstraints = {
      audio: false,
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { max: 30 },
        facingMode: { exact: "environment" }, // exactをidealに変更
      },
    };

    const decodeQrCode = () => {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (canvas && video) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const qrCodeData = jsQR(
            imageData.data,
            imageData.width,
            imageData.height,
          );
          if (qrCodeData) {
            setResult(qrCodeData.data);
            return;
          }
          setTimeout(decodeQrCode, 200);
        }
      }
    };

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play();
            decodeQrCode();
          };
        }
      })
      .catch((err) => {
        console.error("Error accessing media devices:", err);
        setError(err.name + ": " + err.message);
      });

    const currentVideoRef = videoRef.current;

    return () => {
      if (currentVideoRef && currentVideoRef.srcObject) {
        const stream = currentVideoRef.srcObject as MediaStream;
        const tracks = stream.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (!result) return;

    const handleVisitorRegister = async () => {
      try {
        const visitorData = await readVisitor({ visitor_id: result });

        if ("detail" in visitorData) {
          // 登録されていない
          setMessage("登録されていないQRコードです");
          return;
        } else {
          // 登録されている
          const today = new Date().getDate();
          const day = today === 1 ? "first" : "second";

          await upsertVisited({
            visitor_id: result,
            day: day,
            visited: true,
          });
          // カメラ停止
          if (videoRef.current && videoRef.current.srcObject) {
            const stream = videoRef.current.srcObject as MediaStream;
            stream.getTracks().forEach((track) => track.stop());
          }
          setCompleted(true);
        }
      } catch (error) {
        console.error("Error handling visitor:", error);
      }
    };

    handleVisitorRegister();
  }, [result]);

  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      minH="100vh"
      bg="gray.50"
      gap={6}
    >
      <Text m={4} fontSize="xl" fontWeight="bold">
        {message}
      </Text>

      <Box
        border="2px dashed"
        borderColor="#ECA517FF"
        borderRadius="md"
        w="80vw"
        h="50vh"
        position="relative"
        overflow="hidden"
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
        <canvas
          ref={canvasRef}
          width="auto"
          height="auto"
          style={{ display: "none" }}
        />
      </Box>

      {error && (
        <Text color="red.500" fontWeight="bold">
          {error}
        </Text>
      )}

      {completed && (
        <Box
          position="fixed"
          top={0}
          left={0}
          w="100vw"
          h="100vh"
          bg="blackAlpha.600"
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={9999}
        >
          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            boxShadow="lg"
            textAlign="center"
            w="80%"
            maxW="400px"
          >
            <Text fontSize="xl" fontWeight="bold" mb={4}>
              チェックイン完了 🎉
            </Text>
            <Text mb={6}>ご来場ありがとうございます！</Text>
            <Flex justify="center">
              <Button colorScheme="teal" onClick={handleReturnHome}>
                戻る
              </Button>
            </Flex>
          </Box>
        </Box>
      )}
    </Flex>
  );
}

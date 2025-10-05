"use client";

import { Button, Flex } from "@chakra-ui/react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const handleScanPage = () => {
    router.push("/scan");
  };

  return (
    <Flex minH="100vh" align="center" justify="center">
      <Button colorScheme="teal" onClick={handleScanPage}>
        QRスキャン
      </Button>
    </Flex>
  );
}

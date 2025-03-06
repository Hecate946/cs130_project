import React from "react";
import { Button, Alert } from "react-native";
import { useRouter } from "expo-router";
import { getDeviceId } from "@/components/recreation/DeviceId";
import { Platform } from "react-native";

const BACKEND_HOST = Platform.OS === "android" ? "http://10.0.2.2:5001/api" : "http://localhost:5001/api";
const LOGOUT_URL = `${BACKEND_HOST}/v1/rec/logout`;

export default function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    const deviceId = await getDeviceId();
    try {
      const response = await fetch(LOGOUT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ device_id: deviceId }),
      });

      if (!response.ok) throw new Error(`Logout failed with status ${response.status}`);

      const data = await response.json();
      console.log("Logout response:", data);
      Alert.alert("Logged out", "You have been logged out of My UCLA.");
      // Redirect to main page
      router.push("/");
    } catch (error) {
      console.error("Error logging out:", error);
      Alert.alert("Error", "Logout failed. Please try again.");
    }
  };

  return <Button title="Log out of my UCLA" onPress={handleLogout} />;
}

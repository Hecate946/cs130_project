import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";
import React, { useState, useEffect, useCallback } from "react";
import { TouchableOpacity } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "@react-navigation/native";

interface NotificationBellProps {
  facilityName: string;
}

export default function NotificationBell({ facilityName }: NotificationBellProps) {
  const [hasNotifications, setHasNotifications] = useState(false);

  const checkNotifications = async () => {
    try {
      console.log("-------------------------")
      console.log("curr facility", facilityName)
      const keys = await AsyncStorage.getAllKeys();
      console.log("all keys", keys)
      const facilityKeys = keys.filter((key) => key.startsWith(`notification_${facilityName}`));
      console.log("facility keys", keys)
      const values = await AsyncStorage.multiGet(facilityKeys);
      console.log("values", values)
      const anyOn = values.some(([, value]) => value === "on");
      console.log("any on", anyOn)

      setHasNotifications(anyOn);
    } catch (error) {
      console.error("Error checking notifications:", error);
    }
  };

  useFocusEffect(
    useCallback(() => {
      checkNotifications();
    }, [facilityName])
  );

  return (
    <TouchableOpacity onPress={checkNotifications}> //TODO fix when combine with modal.
      <MaterialCommunityIcons
        name={hasNotifications ? "bell-check-outline" : "bell-off-outline"}
        size={32}
        color="black"
      />
    </TouchableOpacity>
  );
};
import { StyleSheet, Text, View } from "react-native";
import { Switch } from 'react-native-paper';
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

interface NotificationItemProps {
  name: string,
  id: string,
};

export default function NotificationItem({name, id} : NotificationItemProps) {

  const [isSwitchOn, setIsSwitchOn] = useState(false);

  useEffect(() => {
    const loadSwitchState = async () => {
      const storedValue = await AsyncStorage.getItem(`notification_${id}`);
      setIsSwitchOn(storedValue === "on");
    };

    loadSwitchState();
  }, []);

  const onToggleSwitch = async () => {
    const newValue = !isSwitchOn ? "on" : "off";
    setIsSwitchOn(!isSwitchOn);

    await AsyncStorage.setItem(`notification_${id}`, newValue);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.itemText}>
        {name}
      </Text>
      <Switch
        color={Colors.light.tint}
        value={isSwitchOn}
        onValueChange={onToggleSwitch}
      >
      </Switch>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    backgroundColor: "white",
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    width: "100%",
    borderRadius: 10,
  },

  itemText: {
    fontSize: 16,
    fontWeight: 300,
  },

  switch: {
    color: Colors.light.icon,
    borderRadius: 60,
  },

  buttonLabel: {
    fontSize: 18,
    color: Colors.light.text,
  },

  buttonContent: {
    height: 64,
    width: 180,
    justifyContent: "center",
    alignItems: "center",
  },
});

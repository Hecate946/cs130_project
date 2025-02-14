import { Pressable, StyleSheet, Text, View } from "react-native";
import { Switch } from 'react-native-paper';
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

interface NotificationItemProps {
  name: string,
  id: string,
};

export default function NotificationItem({name, id} : NotificationItemProps) {
  //Example: const [enabled, setEnabled] = useState(false); 

  const [isSwitchOn, setIsSwitchOn] = useState(false); //I will call setEnabled, which invokes useState which will do the hard work for me.
  //"enabled" is the boolean that holds the actual value.

  const onToggleSwitch = async () => {
    const newValue = !isSwitchOn ? "on" : "off";

    await AsyncStorage.setItem(`notification_${id}`, newValue);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  
    setIsSwitchOn(!isSwitchOn);
  };

  return (
    <View style={styles.container}>
      <Text> 
        {name}
      </Text>
      <Switch
        color={Colors.dark.icon}
        value={isSwitchOn} 
        onValueChange={onToggleSwitch} 
      >
      </Switch>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row", // Places items in a row
    alignItems: "center", // Aligns items vertically
    justifyContent: "space-between", // Pushes items to the edges
    padding: 16,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    width: "100%",
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

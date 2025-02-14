import { Pressable, StyleSheet, Text, View } from "react-native";
import { Switch } from 'react-native-paper';
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState } from "react";

interface NotificationItemProps {
  name: string,
};

export default function NotificationItem({name} : NotificationItemProps) {
  //Example: const [enabled, setEnabled] = useState(false); 

  const [isSwitchOn, setIsSwitchOn] = useState(false); //I will call setEnabled, which invokes useState which will do the hard work for me.
  //"enabled" is the boolean that holds the actual value.

  const onToggleSwitch = async () => {
    setIsSwitchOn(!isSwitchOn);
    //TODO: Access local storage to save this notification preference.
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

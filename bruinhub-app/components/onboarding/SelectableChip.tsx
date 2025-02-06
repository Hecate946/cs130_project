import AsyncStorage from "@react-native-async-storage/async-storage";
import { StyleSheet } from "react-native";
import { Chip } from "react-native-paper";
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState } from "react";

interface SelectableChipProps {
  name: string,
  id: string,
};

export default function SelectableChip({name, id} : SelectableChipProps) {
  const [selected, setSelected] = useState(false);

  const handlePress = async () => {
    // Access local storage to save preferences
    if (selected) {
      await AsyncStorage.removeItem(`pin_${id}`);
    } else {
      await AsyncStorage.setItem(`pin_${id}`, "true");
    }
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); // Light, Medium, Heavy
    setSelected(!selected);
  };
  
  return (
    <Chip
      mode="outlined"
      selected={selected}
      onPress={handlePress}
      showSelectedCheck={false}
      style={selected ? styles.selectedChip : styles.unselectedChip}
      textStyle={selected ? styles.selectedText : styles.unselectedText}
    >
      {name}
    </Chip>
  );
};

const styles = StyleSheet.create({
  selectedChip: {
    backgroundColor: Colors.light.shade,
    borderRadius: 50,
    width: "auto",
    alignSelf: "center",
  },

  unselectedChip: {
    backgroundColor: Colors.light.icon,
    borderRadius: 50,
    width: "auto",
    borderColor: Colors.light.shade,
    alignSelf: "center",
  },

  selectedText: {
    color: Colors.light.background,
    paddingTop: 5,
    paddingBottom: 5,
    paddingRight: 10,
    paddingLeft: 10,
    fontSize: 16,
  },

  unselectedText: {
    color: Colors.light.shade,
    paddingTop: 5,
    paddingBottom: 5,
    paddingRight: 10,
    paddingLeft: 10,
    fontSize: 16,
  },

});
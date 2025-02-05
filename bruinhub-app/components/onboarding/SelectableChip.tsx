import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Button, FAB, Chip } from "react-native-paper";
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState } from "react";

interface SelectableChipProps {
  name: string,
};

export default function SelectableChip({name} : SelectableChipProps) {
  const [selected, setSelected] = useState(false);

  const handlePress = async () => {
    // Access local storage to save preferences
  };
  
  return (
    <Chip
      mode="outlined"
      selected={selected}
      onPress={handlePress}
    >
      {name}
    </Chip>
  );
};
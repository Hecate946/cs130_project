import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { Text, View } from "react-native";
import { Button } from "react-native-paper";
import { useEffect, useState } from "react";
import { CategoriesMap } from "@/constants/CategoriesMap";

interface HomeScreenProps {
  onFinish: () => void;
};

export default function HomeScreen({ onFinish }: HomeScreenProps) {
  const [pins, setPins] = useState<string[]>([])

  const getAllPins = async () => {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const pinnedKeys = keys.filter((key) => key.startsWith("pin_"));
      return pinnedKeys.map((key) => {
        const id = key.replace("pin_", "");

        for (const [, subMap] of CategoriesMap) {
          if (subMap.has(id)) {
            return subMap.get(id);
          }
        }
        return "";
      });
    } catch (e) {
      console.log("Error getting all pins: ", e);
      return [];
    }
  };

  useEffect(() => {
    const loadPinnedItems = async () => {
      const items = await getAllPins();
      setPins(items.filter((item): item is string => item !== undefined));
    };
    loadPinnedItems();
  }, []);


  // TODO: REMOVE this function and onFinish prop
  // FOR TESTING/DEV PURPOSES -- RETURN TO ONBOARDING SCREEN
  // THIS METHOD ALSO CLEARS ALL PINS
  const handleFinish = async () => {
    await AsyncStorage.setItem("finishedOnboarding", "false");

    const keys = await AsyncStorage.getAllKeys();
    const pinnedKeys = keys.filter((key) => key.startsWith("pin_"));
    await AsyncStorage.multiRemove(pinnedKeys);

    onFinish();
  };


  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {
        pins.map((item) => (
          <Text key={item}>{item}</Text>
        ))
      }
      <Text>This is the home screen</Text>
      <Link href="/" asChild>
        <Button mode="contained" onPress={handleFinish}>
            Back to onboarding for dev purposes
        </Button>
      </Link>
      <Link href="/NotificationsScreen" asChild>
        <Button mode="contained">
            To Notifs
        </Button>
      </Link>
    </View>
  );
}

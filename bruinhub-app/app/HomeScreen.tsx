import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { Button, Searchbar } from "react-native-paper";
import { useEffect, useState } from "react";
import { CategoriesMap } from "@/constants/CategoriesMap";
import HomeCard from "@/components/home/HomeCard";
import * as Haptics from "expo-haptics";
import { Colors } from "@/constants/Colors";
import Divider from "@/components/Divider";
import Fuse from "fuse.js"; // Fuzzy searching!!!

interface HomeScreenProps {
  onFinish: () => void;
};

export default function HomeScreen({ onFinish }: HomeScreenProps) {
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());
  const [allItems, setAllItems] = useState<{ id: string; name: string }[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  const loadPinnedItems = async () => {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const pinnedIds = new Set(
        keys.filter((key) => key.startsWith("pin_")).map((key) => key.replace("pin_", ""))
      );
      setPinnedItems(pinnedIds);
    } catch (error) {
      console.log("Error loading pinned items:", error);
    }
  };

  const loadAllItems = () => {
    const items = Array.from(CategoriesMap.values()).flatMap((subMap) =>
      Array.from(subMap.entries()).map(([id, name]) => ({ id, name }))
    );
    setAllItems(items);
  };

  const togglePin = async (id: string) => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const pinAsyncStorageKey = `pin_${id}`;

    try {
      if (pinnedItems.has(id)) {
        await AsyncStorage.removeItem(pinAsyncStorageKey);
      } else {
        await AsyncStorage.setItem(pinAsyncStorageKey, "true");
      }

      // Refresh pinned items
      loadPinnedItems();
    } catch (error) {
      console.log("Error toggling pin:", error);
    }
  };

  useEffect(() => {
    loadPinnedItems();
    loadAllItems();
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

  // Threshold sent to 0.25 through visual inspection and testing. Can change in future as well
  const fuse = new Fuse(allItems, {
    keys: ["name"],
    threshold: 0.25,
    includeScore: false,
  });

  const filteredItems = searchQuery
    ? fuse.search(searchQuery).map((result) => result.item)
    : allItems;

  const filteredPinned = filteredItems.filter((item) => pinnedItems.has(item.id));
  const filteredUnpinned = filteredItems.filter((item) => !pinnedItems.has(item.id));

  return (
    <View
      style={styles.container}
    >
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
        keyboardShouldPersistTaps="handled"
      >
        <Searchbar
          placeholder="Search"
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.search}
        />
        <Divider name="Pinned" />
        {
          filteredPinned.map((item) => (
            <HomeCard
              name={item.name}
              description={item.name}
              isPinned={true}
              pinCallback={() => togglePin(item.id)}
              key={item.id}
            />
          ))
        }
        <Divider name="The Rest" />
        {
          filteredUnpinned.map((item) => (
            <HomeCard
              name={item.name}
              description={item.name}
              isPinned={false}
              pinCallback={() => togglePin(item.id)}
              key={item.id}
            />
          ))
        }
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
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "flex-start",
    alignItems: "center",
    backgroundColor: Colors.light.background,
    width: "100%",
    paddingTop: 80, // TODO CHANGE LATER
  },

  scrollContainer: {
    flex: 1,
    width: "100%",
  },

  contentContainer: {
    flexGrow: 1,
    paddingBottom: 155,
    marginStart: 20,
    marginEnd: 20,
  },

  search: {
    backgroundColor: Colors.light.icon,
  },
});

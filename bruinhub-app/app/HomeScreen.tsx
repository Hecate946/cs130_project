import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link, useRouter } from "expo-router";
import { ScrollView, StyleSheet, Text, View, Image, TouchableOpacity, Keyboard } from "react-native";
import { Button, Searchbar } from "react-native-paper";
import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";
import { useEffect, useState } from "react";
import * as Haptics from "expo-haptics";
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

import { CategoriesMap } from "@/constants/CategoriesMap";
import { Colors } from "@/constants/Colors";
import HomeCard from "@/components/home/HomeCard";
import Divider from "@/components/Divider";
import FacilityModal from "@/components/modal/FacilityModal";
import { SlugMap } from '@/constants/SlugMap';

import Fuse from "fuse.js"; // Fuzzy searching!!!

// Set up notifications handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

interface HomeScreenProps {
  onFinish: () => void;
};

interface AllFacilityData {
  data: Record<string, {
    hours?: string;
    capacity?: number;
    occupants?: number;
  }>;
}

const HOURS_OCCUP_URL = "http://192.168.98.104:5001/api/v1/hours-and-occupancy"; //TODO fix as needed.

export default function HomeScreen({ onFinish }: HomeScreenProps) {
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());
  const [allItems, setAllItems] = useState<{ id: string; name: string }[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFacility, setSelectedFacility] = useState("");
  const [modalVisible, setModalVisible] = useState(false);
  const [facilityData, setFacilityData] = useState<AllFacilityData>({ data: {} });

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

  const getTodayHours = (hours: Record<string, string>) => {
    const today = new Date().toLocaleDateString("en-US", { weekday: "long" });
    return hours?.[today] ?? "Hours Unavailable";
  };

  const fetchHoursAndCapacity = async () => {
    try {
      const response = await fetch(HOURS_OCCUP_URL);
      if (!response.ok) {
        throw new Error(`HTTP Error with Status: ${response.status}`);
      }

      const jsonResponse = await response.json();
      const parsedFacilities: AllFacilityData = { data: {} };

      Object.keys(jsonResponse.data).forEach((facilityKey) => {
        const facility = jsonResponse.data[facilityKey];
        let formattedHours = "Hours Unavailable";
        if (Array.isArray(facility.hours)) { //Hours are usually the same every day.
          formattedHours = `${facility.hours.join(", ")}`;
        }
        else if (typeof facility.hours === "object"){ //Hours for Gym differs Daily
          formattedHours = getTodayHours(facility.hours);
        }

        parsedFacilities.data[facilityKey] = {
          capacity: facility.capacity ?? 0,
          occupants: facility.occupants ?? 0,
          hours: formattedHours ?? "",
        };
      });
      setFacilityData(parsedFacilities);
    } catch (error) {
      console.error("Error fetching facility data:", error);
    }
  };

  useEffect(() => {
    loadPinnedItems();
    loadAllItems();
    fetchHoursAndCapacity();
  }, []);

  const handleOpenModal = (facilityName: string) => {
    setSelectedFacility(facilityName);
    setModalVisible(true);
    Keyboard.dismiss();
    setSearchQuery("");
  };

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

  // Threshold sent to 0.25 through visual inspection and testing, can be changed
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

  const router = useRouter();
  const goToNotifications = () => {
    router.push("/NotificationsScreen");
  }

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.bannerContainer}>
          <Image
            source={require("../assets/images/BruinHub.png")}
            style={{ width: 200, height: 50, borderRadius: 2 }}
          />
          <TouchableOpacity testID="home-screen-notif-button" onPress={goToNotifications}>
            <MaterialCommunityIcons
              name={"bell-outline"}
              size={32}
              color="black"
            />
          </TouchableOpacity>
        </View>
        <Searchbar
          placeholder="Search"
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchBar}
          inputStyle={styles.searchBarInput}
        />
        <Divider name="Pinned" />
        {
          filteredPinned.length > 0 ? (
            filteredPinned.map((item) => {
              const facilityKey = item.name;
              const facName = SlugMap.get(facilityKey) ?? facilityKey;
              const facilityInfo = facilityData?.data?.[facName] ?? {};
              const hours = facilityInfo?.hours ?? "";

              return (
                <HomeCard
                  name={item.name}
                  description={hours}
                  facilityData={facilityInfo}
                  isPinned={true}
                  pinCallback={() => togglePin(item.id)}
                  key={item.id}
                  onPress={() => handleOpenModal(item.name)}
                />
              );
            })):(
          <Text style={styles.pinText}>Pin your favorite spots!</Text>)
        }
        <Divider name="The Rest" />
        {
          filteredUnpinned.map((item) => {
            const facilityKey = item.name;
            const facName = SlugMap.get(facilityKey) ?? facilityKey;
            const facilityInfo = facilityData?.data?.[facName] ?? {};
            const hours = facilityInfo?.hours ?? "";

            return (
              <HomeCard
                name={item.name}
                description={hours}
                facilityData={facilityInfo}
                isPinned={false}
                pinCallback={() => togglePin(item.id)}
                key={item.id}
                onPress={() => handleOpenModal(item.name)}
              />
            );
          })
        }
        <Link href="/" asChild>
          <Button mode="contained" onPress={handleFinish}>
            Back to onboarding for dev purposes
          </Button>
        </Link>
        <FacilityModal
          visible={modalVisible}
          onClose={() => setModalVisible(false)}
          facility={selectedFacility}
        />
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
    paddingTop: 70,
  },

  scrollContainer: {
    flex: 1,
    width: "100%",
  },

  bannerContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingBottom: 20,
  },

  pinText: {
    fontStyle: "italic",
    alignSelf: "center",
  },

  contentContainer: {
    flexGrow: 1,
    paddingBottom: 40,
    marginStart: 20,
    marginEnd: 20,
  },

  searchBar: {
    backgroundColor: Colors.light.icon,
    borderRadius: 40,
    elevation: 1,
  },

  searchBarInput: {
    fontSize: 16,
    paddingVertical: 0,
    minHeight: 10,
  },
});

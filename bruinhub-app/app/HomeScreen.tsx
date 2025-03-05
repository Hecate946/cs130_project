import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link, useRouter } from "expo-router";
import { ScrollView, StyleSheet, Text, View, Image, TouchableOpacity } from "react-native";
import { Button, Searchbar } from "react-native-paper";
import Feather from '@expo/vector-icons/Feather';
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

export default function HomeScreen({ onFinish }: HomeScreenProps) {
  const [pinnedItems, setPinnedItems] = useState<Set<string>>(new Set());
  const [allItems, setAllItems] = useState<{ id: string; name: string }[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFacility, setSelectedFacility] = useState("");
  const [modalVisible, setModalVisible] = useState(false);
  const [expoPushToken, setExpoPushToken] = useState<string>('');
  const [notificationStatus, setNotificationStatus] = useState<string>('');

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

  // Register for push notifications
  const registerForPushNotificationsAsync = async () => {
    try {
      let token;
      
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }
      
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        setNotificationStatus('Permission not granted for notifications');
        return;
      }
      
      token = await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      });
      
      setExpoPushToken(token.data);
      setNotificationStatus('Permission granted! Token: ' + token.data);
      
      // Store token in AsyncStorage for future use
      await AsyncStorage.setItem('expoPushToken', token.data);
      
      // Register this token with our notification service
      try {
        const response = await fetch('http://192.168.216.35:5002/api/notifications/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pushToken: token.data,
            deviceType: Platform.OS,
            preferences: {
              capacity: { enabled: true, threshold: 50 },
              closing: { enabled: true, minutes_before: 30 }
            }
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          setNotificationStatus('Token registered with notification service!');
          console.log('Registration successful:', data);
        } else {
          setNotificationStatus('Failed to register with notification service: ' + data.error);
          console.error('Registration failed:', data);
        }
      } catch (err) {
        console.error('Error registering with notification service:', err);
        setNotificationStatus('Error registering with notification service');
      }
      
    } catch (error) {
      console.log('Error getting push token', error);
      setNotificationStatus('Error: ' + error);
    }
  };

  // Send a test notification from the backend
  const sendTestNotification = async () => {
    try {
      if (!expoPushToken) {
        setNotificationStatus('No push token available. Request permission first.');
        return;
      }
      
      // Send test notification using our notification service
      const response = await fetch('http://192.168.216.35:5002/api/notifications/send-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pushToken: expoPushToken,
          title: 'BruinHub Test',
          message: 'This is a test notification from BruinHub Notification Service!',
          data: {
            screen: 'NotificationsScreen',
            id: Date.now().toString()
          }
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setNotificationStatus('Notification sent successfully!');
        console.log('Notification sent:', data);
      } else {
        setNotificationStatus('Failed to send notification: ' + data.error);
        console.error('Notification failed:', data);
      }
    } catch (error) {
      console.log('Error sending notification', error);
      setNotificationStatus('Error sending notification: ' + error);
    }
  };

  // Simulate capacity notification event
  const simulateCapacityEvent = async () => {
    try {
      const response = await fetch('http://192.168.216.35:5002/api/notifications/simulate-event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eventType: 'capacity',
          facilityName: 'BFit Gym',
          currentCapacity: 40
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setNotificationStatus(`Simulated capacity event. Sent ${data.notifications_sent} notifications.`);
        console.log('Simulation result:', data);
      } else {
        setNotificationStatus('Failed to simulate event: ' + data.error);
        console.error('Simulation failed:', data);
      }
    } catch (error) {
      console.log('Error simulating event', error);
      setNotificationStatus('Error simulating event: ' + error);
    }
  };
  
  // Simulate closing notification event
  const simulateClosingEvent = async () => {
    try {
      const response = await fetch('http://192.168.216.35:5002/api/notifications/simulate-event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eventType: 'closing',
          facilityName: 'Wooden Center',
          minutesUntilClose: 15
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setNotificationStatus(`Simulated closing event. Sent ${data.notifications_sent} notifications.`);
        console.log('Simulation result:', data);
      } else {
        setNotificationStatus('Failed to simulate event: ' + data.error);
        console.error('Simulation failed:', data);
      }
    } catch (error) {
      console.log('Error simulating event', error);
      setNotificationStatus('Error simulating event: ' + error);
    }
  };

  // Load token from AsyncStorage on component mount
  useEffect(() => {
    const loadToken = async () => {
      const token = await AsyncStorage.getItem('expoPushToken');
      if (token) {
        setExpoPushToken(token);
      }
    };
    
    loadToken();
    loadPinnedItems();
    loadAllItems();
  }, []);

  const handleOpenModal = (facilityName: string) => {
    setSelectedFacility(facilityName);
    setModalVisible(true);
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
            source={require("../assets/images/BruinHub.png")} //TODO replace with SVG
            style={{ width: 200, height: 50, borderRadius: 2 }}
          />
          <TouchableOpacity testID="notif-button" onPress={goToNotifications}>
            <Feather
              name="bell"
              size={24}
              color="black"
            />
          </TouchableOpacity>
        </View>
        <Searchbar
          placeholder="Search"
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.search}
        />
        <Divider name="Pinned" />
        {
          filteredPinned.length > 0 ? (
          filteredPinned.map((item) => (
            <HomeCard
              name={item.name}
              description={item.id}
              isPinned={true}
              pinCallback={() => togglePin(item.id)}
              key={item.id}
              onPress={() => handleOpenModal(item.name)}
            />
          ))) :
          <Text style={styles.pinText}>Pin your favorite spots!</Text>
        }
        <Divider name="The Rest" />
        {
          filteredUnpinned.map((item) => (
            <HomeCard
              name={item.name}
              description={item.id}
              isPinned={false}
              pinCallback={() => togglePin(item.id)}
              key={item.id}
              onPress={() => handleOpenModal(item.name)}
            />
          ))
        }
        <Link href="/" asChild>
          <Button mode="contained" onPress={handleFinish}>
            Back to onboarding for dev purposes
          </Button>
        </Link>
        
        <View style={styles.devButtonsContainer}>
          <Text style={styles.devTitle}>Push Notification Dev Tools</Text>
          
          <Button 
            mode="contained" 
            onPress={registerForPushNotificationsAsync}
            style={styles.devButton}
          >
            Request Push Notification Permission
          </Button>
          
          <Button 
            mode="contained" 
            onPress={sendTestNotification}
            style={styles.devButton}
            disabled={!expoPushToken}
          >
            Send Test Notification
          </Button>
          
          <Button 
            mode="contained" 
            onPress={simulateCapacityEvent}
            style={styles.devButton}
            disabled={!expoPushToken}
          >
            Simulate Capacity Notification
          </Button>
          
          <Button 
            mode="contained" 
            onPress={simulateClosingEvent}
            style={styles.devButton}
            disabled={!expoPushToken}
          >
            Simulate Closing Notification
          </Button>
          
          <Text style={styles.statusText}>{notificationStatus}</Text>
        </View>
        
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
    paddingTop: 70, // TODO CHANGE LATER
  },

  scrollContainer: {
    flex: 1,
    width: "100%",
  },

  bannerContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginStart: 10,
    marginEnd: 10,
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

  search: {
    backgroundColor: Colors.light.icon,
  },

  devButtonsContainer: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: Colors.light.icon,
  },
  
  devTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  
  devButton: {
    marginVertical: 5,
  },
  
  statusText: {
    marginTop: 10,
    fontSize: 12,
    color: 'gray',
    textAlign: 'center',
  },
});

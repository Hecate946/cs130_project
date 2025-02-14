import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Link } from "expo-router";
import { Colors } from "@/constants/Colors";
import { Button } from "react-native-paper";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Categories } from "@/constants/Categories";
import NotificationItem from "@/components/notifications/NotificationItem";

const array_categories = ["Fitness", "Dining", "Study Rooms"];
const array_restaurants = [{name: "B-Plate", "id": '0'}, {name: "De Neve", "id": '1'}, {name: "Epicuria", "id": '2'},{name: "The Study", "id": '3'},{name: "Rendezvous", "id": '4'},];

// const Restaurants = Categories.diningHalls;
// const Takeout = Categories.takeout;
// const Gyms = Categories.gym;
// const Libraries = Categories.libraries;
// const ReslifeStudy = Categories.reslifeStudy;
// const ReslifeSpaces = Categories.reslifeSpaces;

export default function NotificationsScreen() {
  return (
    <View style={styles.container}>
      <View style = {styles.leftAlignedText}>
      <Text>Notifications</Text>
      <Text style={styles.bannerText}>Dining Halls</Text>
      </View>
      {array_restaurants.map(function(restaurant) {
      return (
        <View key={restaurant.id}>
          <NotificationItem name={restaurant.name} />
        </View>
      )
      })}
      <Link href="/HomeScreen" asChild>
        <Button 
          style={styles.button} 
          labelStyle={styles.buttonLabel}
          mode="contained">
          <Text>Done</Text>
        </Button>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  leftAlignedText: {
    padding: 12,
    justifyContent: "flex-start", //puts in center of screen up/down wise.
    alignItems: "flex-start",//alignItems: "flex-start", //aligns actual text and buttons to center left/right wise.
    //backgroundColor: Colors.light.background,
    width: "100%"
  },
  container: {
    padding: 12,
    flex: 1,
    justifyContent: "center", //puts in center of screen up/down wise.
    alignItems: "center",//alignItems: "flex-start", //aligns actual text and buttons to center left/right wise.
    backgroundColor: Colors.light.background,
    width: "100%"
  },

  button: {
    marginTop: 20,
    padding: 10,
    height: 64,
    width: 200,
    backgroundColor: Colors.light.icon,
    borderRadius: 60,
  },

  buttonLabel: {
    fontSize: 18,
    color: Colors.light.text,
    alignItems: "center",
  },

  bannerText: {
    height: 64,
    width: 100,
    alignItems: "flex-start",
    color: Colors.dark.icon,
    fontSize: 16,
    fontWeight: "bold",
  },
});

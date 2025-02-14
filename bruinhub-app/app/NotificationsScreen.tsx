import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Link } from "expo-router";
import { Colors } from "@/constants/Colors";
import { Button } from "react-native-paper";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Categories } from "@/constants/Categories";
import NotificationItem from "@/components/notifications/NotificationItem";
import Divider from "@/components/Divider";

//const array_categories = ["Fitness", "Dining", "Study Rooms"];
//const array_restaurants = [{name: "B-Plate", "id": '0'}, {name: "De Neve", "id": '1'}, {name: "Epicuria", "id": '2'},{name: "The Study", "id": '3'},{name: "Rendezvous", "id": '4'},];

const Restaurants = Categories.diningHalls;
const Takeout = Categories.takeout;
const Gyms = Categories.gym;
const Libraries = Categories.libraries;
const ReslifeStudy = Categories.reslifeStudy;
const ReslifeSpaces = Categories.reslifeSpaces;

export default function NotificationsScreen() {
  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
        //keyboardShouldPersistTaps="handled"
      >
        <View style={styles.welcomeContainer}>
          <Text style={styles.title}>Notifications</Text>
          <Text style={styles.text}>Select the facilities you'd like to receive 
            notifications for, including hours updates and holiday reminders.</Text>
        </View>

        <Divider name="Restaurants" />
        <View /*style={styles.chipContainer}*/>
          {Restaurants.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View> 

        <Divider name="Takeout" />
        <View /*style={styles.chipContainer}*/>
          {Takeout.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View>

        <Divider name="Gyms" />
        <View /*style={styles.chipContainer}*/>
          {Gyms.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View>

        <Divider name="Libraries" />
        <View /*style={styles.chipContainer}*/>
          {Libraries.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Study Rooms" />
        <View /*style={styles.chipContainer}*/>
          {ReslifeStudy.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Spaces" />
        <View /*style={styles.chipContainer}*/>
          {ReslifeSpaces.map((item) => (
            <NotificationItem name={item.name} key={item.key}/>
          ))}
        </View>

      </ScrollView>
      <View style={{ position: "absolute", bottom: 50 }}>
        <Link href="/" asChild>
          <Button
            style={styles.button}
            //onPress={handleFinish}
            uppercase={true}
            mode="elevated"
            //contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
          >
            Done
          </Button>
        </Link>
      </View>
    </View>
  );
  /*return (
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
  ); */
}

const styles = StyleSheet.create({
  container: {
    //padding: 12,
    flex: 1,
    justifyContent: "flex-start", //puts in center of screen up/down wise.
    alignItems: "center",//alignItems: "flex-start", //aligns actual text and buttons to center left/right wise.
    backgroundColor: Colors.light.background,
    width: "100%",
    paddingTop: 80, //TODO CHANGE LATER
  },

  scrollContainer: {
    flex: 1,
  },

  contentContainer: {
    flexGrow: 1,
    paddingBottom: 155,
    marginStart: 20,
    marginEnd: 20,
  },

  welcomeContainer: {
    backgroundColor: Colors.light.background,
    width: "100%",
    gap: 5,
  },
  
  title: {
    fontSize: 24,
    fontWeight: 400,
    textTransform: "uppercase",
  },

  text: {
    fontSize: 16,
    fontWeight: 300,
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

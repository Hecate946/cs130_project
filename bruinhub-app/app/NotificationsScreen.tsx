import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Link } from "expo-router";
import { Colors } from "@/constants/Colors";
import { Button } from "react-native-paper";
import * as Haptics from "expo-haptics";import { Categories } from "@/constants/Categories";
import NotificationItem from "@/components/notifications/NotificationItem";
import Divider from "@/components/Divider";

const Restaurants = Categories.diningHalls;
const Takeout = Categories.takeout;
const Gyms = Categories.gym;
const Libraries = Categories.libraries;
const ReslifeStudy = Categories.reslifeStudy;
const ReslifeSpaces = Categories.reslifeSpaces;

interface NotificationsScreenProps {
  onFinish: () => void;
};

export default function NotificationsScreen({ onFinish }: NotificationsScreenProps) {
  
  const handleFinish = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    onFinish();
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
      >
        <View style={styles.welcomeContainer}>
          <Text style={styles.title}>Notifications</Text>
          <Text style={styles.text}>Select the facilities you'd like to receive 
            notifications for, including hours updates and holiday reminders.</Text>
        </View>

        <Divider name="Restaurants" />
        <View>
          {Restaurants.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View> 

        <Divider name="Takeout" />
        <View>
          {Takeout.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="Gyms" />
        <View>
          {Gyms.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="Libraries" />
        <View>
          {Libraries.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Study Rooms" />
        <View>
          {ReslifeStudy.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Spaces" />
        <View>
          {ReslifeSpaces.map((item) => (
            <NotificationItem name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

      </ScrollView>
      <View style={{ position: "absolute", bottom: 50 }}>
        <Link href="/" asChild>
          <Button
            style={styles.button}
            onPress={handleFinish}
            uppercase={true}
            mode="elevated"
            labelStyle={styles.buttonLabel}
          >
            Done
          </Button>
        </Link>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
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

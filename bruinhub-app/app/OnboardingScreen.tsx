import AsyncStorage from "@react-native-async-storage/async-storage";
import { Link } from "expo-router";
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
import { Button, FAB } from "react-native-paper";
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";

import { Categories } from "@/constants/Categories";
import Divider from "@/components/Divider";
import SelectableChip from "@/components/onboarding/SelectableChip";

interface OnboardingScreenProps {
  onFinish: () => void;
};

const Restaurants = Categories.diningHalls;
const Takeout = Categories.takeout;
const Gyms = Categories.gym;
const Libraries = Categories.libraries;
const ReslifeStudy = Categories.reslifeStudy;
const ReslifeSpaces = Categories.reslifeSpaces;

export default function OnboardingScreen({ onFinish }: OnboardingScreenProps) {

  const handleFinish = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy); // Light, Medium, Heavy
    await AsyncStorage.setItem("finishedOnboarding", "true");
    onFinish();
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.welcomeContainer}>
          <Text style={styles.title}>Welcome</Text>
          <Text style={styles.text}>Choose your favorite spots to pin!</Text>
        </View>

        <Divider name="Restaurants" />
        <View style={styles.chipContainer}>
          {Restaurants.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="Takeout" />
        <View style={styles.chipContainer}>
          {Takeout.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="Gyms" />
        <View style={styles.chipContainer}>
          {Gyms.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="Libraries" />
        <View style={styles.chipContainer}>
          {Libraries.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Study Rooms" />
        <View style={styles.chipContainer}>
          {ReslifeStudy.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
          ))}
        </View>

        <Divider name="ResLife Spaces" />
        <View style={styles.chipContainer}>
          {ReslifeSpaces.map((item) => (
            <SelectableChip name={item.name} key={item.key} id={item.key}/>
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
            contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
          >
            Let's Go
          </Button>
        </Link>
      </View>
    </View>
  );
};

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

  chipContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: "8",
    justifyContent: "center",
    alignItems: "center",
  },

  button: {
    backgroundColor: Colors.light.shade,
    borderRadius: 60,
  },

  buttonLabel: {
    fontSize: 18,
    color: Colors.light.background,
  },

  buttonContent: {
    height: 64,
    width: 180,
    justifyContent: "center",
    alignItems: "center",
  },
});

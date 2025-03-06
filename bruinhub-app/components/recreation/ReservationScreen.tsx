import React, { useCallback, useState } from 'react';
import { View, Modal, Platform } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import LoginWebView from './LoginWebView';
import ReservationInterface from './ReservationInterface';
import { getDeviceId } from './DeviceId';

const BACKEND_HOST =
  Platform.OS === 'android' ? 'http://10.0.2.2:5001/api' : 'http://localhost:5001/api';
const AUTH_CHECK_URL = `${BACKEND_HOST}/v1/rec/check-auth`;

const ReservationScreen: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [showLogin, setShowLogin] = useState<boolean>(false);

  // Re-run the auth check every time the screen comes into focus
  useFocusEffect(
    useCallback(() => {
      const checkAuth = async () => {
        const deviceId = await getDeviceId();
        try {
          const response = await fetch(`${AUTH_CHECK_URL}?deviceId=${deviceId}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          });
          if (!response.ok)
            throw new Error(`Auth check failed with status ${response.status}`);

          const data = await response.json();
          console.log('Auth check response:', data);
          if (data.authenticated) {
            setIsAuthenticated(true);
            setShowLogin(false);
          } else {
            setIsAuthenticated(false);
            setShowLogin(true);
          }
        } catch (error) {
          console.error('Error checking auth:', error);
          setIsAuthenticated(false);
          setShowLogin(true);
        }
      };

      checkAuth();

      // Cleanup function (if needed)
      return () => {};
    }, [])
  );

  const handleLoginSuccess = (): void => {
    setShowLogin(false);
    setIsAuthenticated(true);
  };

  return (
    <View style={{ flex: 1 }}>
      {showLogin && (
        <Modal visible={showLogin} animationType="slide">
          <LoginWebView onLoginSuccess={handleLoginSuccess} />
        </Modal>
      )}
      {isAuthenticated && <ReservationInterface />}
    </View>
  );
};

export default ReservationScreen;

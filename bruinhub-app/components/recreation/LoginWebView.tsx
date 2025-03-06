import React, { useEffect, useState } from 'react';
import { Platform } from 'react-native';
import { WebView, WebViewNavigation } from 'react-native-webview';
import CookieManager from '@react-native-cookies/cookies';
import { getDeviceId } from './DeviceId';

interface LoginWebViewProps {
  onLoginSuccess: () => void;
}

// Dynamically set the backend URL based on the platform
const BACKEND_HOST =
  Platform.OS === 'android' ? 'http://10.0.2.2:5001/api' : 'http://localhost:5001/api';
const LOGIN_URL = 'https://secure.recreation.ucla.edu/account/login';
const SENTINEL_URL = 'https://secure.recreation.ucla.edu/account/IsAuthenticated'; // Sentinel API used to verify login status quickly
const BACKEND_URL = `${BACKEND_HOST}/v1/rec/login`; // Backend login endpoint
const AUTH_CHECK_URL = `${BACKEND_HOST}/v1/rec/check-auth`; // Backend auth check endpoint

const LoginWebView: React.FC<LoginWebViewProps> = ({ onLoginSuccess }) => {
  const [showWebView, setShowWebView] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Step 2: Check if the user is already logged in by querying the backend auth endpoint
    const checkAuthentication = async () => {
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

        // Step 3: If backend indicates the user is authenticated, proceed
        if (data.authenticated) {
          console.log('✅ User is already authenticated.');
          setIsAuthenticated(true);
          onLoginSuccess();
        } else {
          // Step 4: If not authenticated, verify using the sentinel endpoint
          console.log('🔍 User not authenticated, verifying via IsAuthenticated API...');
          verifySentinel();
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        // If the auth check fails, assume not authenticated and show the WebView
        setShowWebView(true);
      }
    };

    checkAuthentication();
  }, []);

  // Step 5: Verify login by calling the sentinel endpoint
  const verifySentinel = async () => {
    try {
      const response = await fetch(SENTINEL_URL, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        // If sentinel confirms authentication, proceed to extract the cookie
        if (data.IsAuthenticated) {
          console.log('✅ Sentinel detected: User is logged in.');
          handleSuccessfulLogin();
          return;
        }
      }
      // Step 4 (continued): If sentinel check fails, display the WebView for login
      console.log('❌ Sentinel check failed: Showing login WebView.');
      setShowWebView(true);
    } catch (error) {
      console.error('Error checking sentinel:', error);
      setShowWebView(true);
    }
  };

  // Step 6, 7 & 8: Extract the authentication cookie and send it to the backend for confirmation
  const handleSuccessfulLogin = async () => {
    const deviceId = await getDeviceId();

    try {
      const cookies = await CookieManager.get(
        'https://secure.recreation.ucla.edu/'
      );
      const aspCookie = cookies['.AspNet.ApplicationCookie'];

      if (aspCookie) {
        console.log('🍪 AspNet Application Cookie found:', aspCookie.value);

        // Step 7: Send the device ID and cookie to the backend login endpoint
        const response = await fetch(BACKEND_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: deviceId,
            aspnet_cookie: aspCookie.value,
          }),
        });

        if (!response.ok)
          throw new Error(`Login failed with status ${response.status}`);

        const data = await response.json();
        console.log('Backend login response:', data);

        // Step 8: If backend confirms the login, mark as authenticated and trigger onLoginSuccess
        if (data.success) {
          console.log('✅ Backend confirmed login.');
          setIsAuthenticated(true);
          onLoginSuccess();
        } else {
          console.log('⚠️ Backend did not validate session:', data);
        }
      } else {
        console.log('❌ AspNet Application Cookie not found.');
      }
    } catch (error) {
      console.error('Error sending cookie to backend:', error);
    }
  };

  // Step 5: If the user is not logged in, the WebView will be displayed for them to log in
  return showWebView ? (
    <WebView
      source={{ uri: LOGIN_URL }}
      onNavigationStateChange={(navState: WebViewNavigation) => {
        // Use the sentinel check when the URL is related to UCLA Rec.
        if (navState.url.includes('secure.recreation.ucla.edu')) {
          // We trigger the login confirmation process once user navigates within UCLA Rec.
          handleSuccessfulLogin();
        }
      }}
    />
  ) : null;
};

export default LoginWebView;

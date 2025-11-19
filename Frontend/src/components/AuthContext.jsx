// 'use client';
// import React, { createContext, useState, useEffect } from 'react';
// import AxiosInstance from "@/components/AxiosInstance";

// export const AuthContext = createContext();

// export const AuthProvider = ({ children }) => {
//   console.log('AuthProvider is rendered');

//   const [token, setToken] = useState(null);
//   const [refreshToken, setRefreshToken] = useState(null);
//   const [permissions, setPermissions] = useState([]);
//   const [role, setRole] = useState(null);
//   const [user, setUser] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     // Load data from localStorage on mount
//     const storedToken = localStorage.getItem('access_token');
//     const storedRefreshToken = localStorage.getItem('refresh_token');
//     const storedPermissions = localStorage.getItem('permissions');
//     const storedRole = localStorage.getItem('role');
//     const storedUser = localStorage.getItem('user');

//     console.log('Loading auth data from localStorage...');

//     if (storedToken) {
//       setToken(storedToken);
//       console.log('Loaded access token');
//     }

//     if (storedRefreshToken) {
//       setRefreshToken(storedRefreshToken);
//     }

//     if (storedPermissions) {
//       try {
//         const parsedPermissions = JSON.parse(storedPermissions);
//         setPermissions(parsedPermissions);
//         console.log('Loaded permissions:', parsedPermissions);
//       } catch (error) {
//         console.error('Error parsing permissions:', error);
//         setPermissions([]);
//       }
//     }

//     if (storedRole) {
//       try {
//         const parsedRole = JSON.parse(storedRole);
//         setRole(parsedRole);
//         console.log('Loaded role:', parsedRole);
//       } catch (error) {
//         console.error('Error parsing role:', error);
//         setRole(null);
//       }
//     }

//     if (storedUser) {
//       try {
//         const parsedUser = JSON.parse(storedUser);
//         setUser(parsedUser);
//         console.log('Loaded user:', parsedUser);
//       } catch (error) {
//         console.error('Error parsing user:', error);
//         setUser(null);
//       }
//     }

//     setLoading(false);
//   }, []);

//   const login = (apiResponse) => {
//     console.log('Login function called with response:', apiResponse);
    
//     // Extract data from API response
//     const { data } = apiResponse;
    
//     const accessToken = data.access_token;
//     const refreshTokenValue = data.refresh_token;
//     const userPermissions = data.permissions || [];
//     const userRole = data.Role;
//     const userData = {
//       id: data.id,
//       name: data.name,
//       username: data.username,
//       email: data.email,
//       mobile: data.mobile,
//       is_superuser: data.is_superuser,
//       profile_image: data.profile_image,
//       role_name: data.role_name,
//       type: data.type,
//       role_id: data.role
//     };

//     // Store in localStorage
//     localStorage.setItem('access_token', accessToken);
//     localStorage.setItem('refresh_token', refreshTokenValue);
//     localStorage.setItem('permissions', JSON.stringify(userPermissions));
//     localStorage.setItem('role', JSON.stringify(userRole));
//     localStorage.setItem('user', JSON.stringify(userData));

//     // Update state
//     setToken(accessToken);
//     setRefreshToken(refreshTokenValue);
//     setPermissions(userPermissions);
//     setRole(userRole);
//     setUser(userData);

//     console.log('Login successful - Data stored:', {
//       token: accessToken ? 'Present' : 'Missing',
//       permissions: userPermissions.length,
//       role: userRole?.name,
//       user: userData.name
//     });
//   };

//   const logout = async () => {
//     try {
//       console.log('Attempting to logout...');
//       // Call logout API
//       await AxiosInstance.post('/user/logout');
//       console.log('Logout API call successful');
//     } catch (error) {
//       console.error('Logout API error:', error);
//     } finally {
//       // Clear localStorage and state regardless of API call success
//       localStorage.removeItem('access_token');
//       localStorage.removeItem('refresh_token');
//       localStorage.removeItem('permissions');
//       localStorage.removeItem('role');
//       localStorage.removeItem('user');

//       setToken(null);
//       setRefreshToken(null);
//       setPermissions([]);
//       setRole(null);
//       setUser(null);

//       console.log('Logged out and cleared all data.');
//     }
//   };

//   // Helper function to check if user has a specific permission
//   const hasPermission = (permission) => {
//     const result = permissions.includes(permission);
//     console.log(`Checking permission "${permission}":`, result);
//     return result;
//   };

//   // Helper function to check multiple permissions (user needs at least one)
//   const hasAnyPermission = (permissionList) => {
//     const result = permissionList.some(permission => permissions.includes(permission));
//     console.log(`Checking any permission from [${permissionList.join(', ')}]:`, result);
//     return result;
//   };

//   // Helper function to check if user has all permissions
//   const hasAllPermissions = (permissionList) => {
//     const result = permissionList.every(permission => permissions.includes(permission));
//     console.log(`Checking all permissions from [${permissionList.join(', ')}]:`, result);
//     return result;
//   };

//   // Check if user is authenticated
//   const isAuthenticated = !!token;

//   // Check if user is superuser
//   const isSuperuser = user?.is_superuser || false;

//   return (
//     <AuthContext.Provider 
//       value={{ 
//         token, 
//         refreshToken,
//         permissions, 
//         role, 
//         user,
//         loading,
//         login, 
//         logout,
//         hasPermission,
//         hasAnyPermission,
//         hasAllPermissions,
//         isAuthenticated,
//         isSuperuser
//       }}
//     >
//       {children}
//     </AuthContext.Provider>
//   );
// };


'use client';
import React, { createContext, useState, useEffect } from 'react';
import AxiosInstance from "@/components/AxiosInstance";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  console.log('AuthProvider is rendered');

  const [token, setToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load data from localStorage on mount
    const storedToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    const storedPermissions = localStorage.getItem('permissions');
    const storedRole = localStorage.getItem('role');
    const storedUser = localStorage.getItem('user');

    console.log('Loading auth data from localStorage...');

    if (storedToken) {
      setToken(storedToken);
      console.log('Loaded access token');
    }

    if (storedRefreshToken) {
      setRefreshToken(storedRefreshToken);
    }

    if (storedPermissions) {
      try {
        const parsedPermissions = JSON.parse(storedPermissions);
        setPermissions(parsedPermissions);
        console.log('Loaded permissions:', parsedPermissions);
      } catch (error) {
        console.error('Error parsing permissions:', error);
        setPermissions([]);
      }
    }

    if (storedRole) {
      try {
        const parsedRole = JSON.parse(storedRole);
        setRole(parsedRole);
        console.log('Loaded role:', parsedRole);
      } catch (error) {
        console.error('Error parsing role:', error);
        setRole(null);
      }
    }

    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        console.log('Loaded user:', parsedUser);
      } catch (error) {
        console.error('Error parsing user:', error);
        setUser(null);
      }
    }

    setLoading(false);
  }, []);

  const login = (apiResponse) => {
    console.log('Login function called with response:', apiResponse);
    
    // Backend returns: { message: "Successful", data: {...}, count: null }
    // Extract data from the nested data object
    const responseData = apiResponse.data;
    
    if (!responseData) {
      console.error('No data in API response');
      return;
    }

    const accessToken = responseData.access_token;
    const refreshTokenValue = responseData.refresh_token;
    const userPermissions = responseData.permissions || [];
    const userRole = responseData.Role;
    const userData = {
      id: responseData.id,
      name: responseData.name,
      username: responseData.username,
      email: responseData.email,
      mobile: responseData.mobile,
      is_superuser: responseData.is_superuser,
      profile_image: responseData.profile_image,
      role_name: responseData.role_name,
      type: responseData.type,
      role_id: responseData.role
    };

    // Validation check
    if (!accessToken || !refreshTokenValue) {
      console.error('Missing tokens in response:', { accessToken, refreshTokenValue });
      return;
    }

    // Store in localStorage
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshTokenValue);
    localStorage.setItem('permissions', JSON.stringify(userPermissions));
    localStorage.setItem('role', JSON.stringify(userRole));
    localStorage.setItem('user', JSON.stringify(userData));

    // Update state
    setToken(accessToken);
    setRefreshToken(refreshTokenValue);
    setPermissions(userPermissions);
    setRole(userRole);
    setUser(userData);

    console.log('Login successful - Data stored:', {
      token: accessToken ? 'Present' : 'Missing',
      permissions: userPermissions.length,
      role: userRole?.name,
      user: userData.name
    });
  };

  const logout = async () => {
    try {
      console.log('Attempting to logout...');
      
      // Backend expects logout data in the request body
      // Check LogoutSerializer to see what fields are needed
      await AxiosInstance.post('/api/user/v1/logout/', {
        // Add any required fields from LogoutSerializer here if needed
      });
      
      console.log('Logout API call successful');
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Clear localStorage and state regardless of API call success
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('permissions');
      localStorage.removeItem('role');
      localStorage.removeItem('user');

      setToken(null);
      setRefreshToken(null);
      setPermissions([]);
      setRole(null);
      setUser(null);

      console.log('Logged out and cleared all data.');
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/Login';
      }
    }
  };

  // Helper function to check if user has a specific permission
  const hasPermission = (permission) => {
    const result = permissions.includes(permission);
    console.log(`Checking permission "${permission}":`, result);
    return result;
  };

  // Helper function to check multiple permissions (user needs at least one)
  const hasAnyPermission = (permissionList) => {
    const result = permissionList.some(permission => permissions.includes(permission));
    console.log(`Checking any permission from [${permissionList.join(', ')}]:`, result);
    return result;
  };

  // Helper function to check if user has all permissions
  const hasAllPermissions = (permissionList) => {
    const result = permissionList.every(permission => permissions.includes(permission));
    console.log(`Checking all permissions from [${permissionList.join(', ')}]:`, result);
    return result;
  };

  // Check if user is authenticated
  const isAuthenticated = !!token;

  // Check if user is superuser
  const isSuperuser = user?.is_superuser || false;

  return (
    <AuthContext.Provider 
      value={{ 
        token, 
        refreshToken,
        permissions, 
        role, 
        user,
        loading,
        login, 
        logout,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
        isAuthenticated,
        isSuperuser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// 'use client';
// import React, { createContext, useState, useEffect } from 'react';
// import AxiosInstance from "@/components/AxiosInstance";

// export const AuthContext = createContext();

// export const AuthProvider = ({ children }) => {
//   console.log('AuthProvider is rendered');
  
//   const [token, setToken] = useState(null);
//   const [permissions, setPermissions] = useState({});

//   useEffect(() => {
//     // This code will only run in the browser
//     const storedToken = localStorage.getItem('token');
//     const storedPermissions = localStorage.getItem('permissions');

//     // Debug logging for loaded data
//     console.log('Loaded token from localStorage:', storedToken);
//     console.log('Loaded permissions from localStorage:', storedPermissions);

//     try {
//       const parsedToken = storedToken ? JSON.parse(storedToken) : null;
//       setToken(parsedToken);
//       console.log('Parsed token:', parsedToken);
//     } catch (error) {
//       console.error('Error parsing token:', error);
//       setToken(null);
//     }

//     try {
//       const parsedPermissions = storedPermissions ? JSON.parse(storedPermissions) : {};
//       setPermissions(parsedPermissions);
//       console.log('Parsed permissions:', parsedPermissions);
//     } catch (error) {
//       console.error('Error parsing permissions:', error);
//       setPermissions({});
//     }
//   }, []);

//   const login = (userToken, userPermissions) => {
//     // Store token and permissions in local storage
//     localStorage.setItem('token', JSON.stringify(userToken));
//     localStorage.setItem('permissions', JSON.stringify(userPermissions));

//     // Update state
//     setToken(userToken);
//     setPermissions(userPermissions || {}); // Ensure it's at least an empty object

//     // Debugging logs
//     console.log('Logged in with token:', userToken);
//     console.log('Permissions set on login:', userPermissions);
//   };

//   const logout = async () => {
//     try {
//       // Assuming you're calling an API to log out
//       await AxiosInstance.post('/user/logout');
      
//       // Clear local storage and update state
//       localStorage.removeItem('token');
//       localStorage.removeItem('permissions');

//       setToken(null);
//       setPermissions({});

//       console.log('Logged out and cleared local storage.');
//     } catch (error) {
//       console.error('Logout error:', error);
//     }
//   };

//   return (
//     <AuthContext.Provider value={{ token, permissions, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };



// 'use client';
// import React, { createContext, useState, useEffect } from 'react';
// import AxiosInstance from "@/components/AxiosInstance";

// export const AuthContext = createContext();

// export const AuthProvider = ({ children }) => {
//   console.log('AuthProvider is rendered');
  
//   const [token, setToken] = useState(null);
//   const [permissions, setPermissions] = useState(undefined);

//   useEffect(() => {
//     const storedToken = localStorage.getItem('token');

//     if (storedToken) {
//       try {
//         const parsedToken = JSON.parse(storedToken);
//         setToken(parsedToken);

//         // Fetch permissions from the backend
//         fetchPermissions(parsedToken);
//       } catch (error) {
//         console.error('Error parsing token:', error);
//         setToken(null);
//       }
//     }
//   }, []);

//   const fetchPermissions = async (token) => {
//     try {
//       const response = await AxiosInstance.get('/user/permissions', {
//         headers: {
//           Authorization: `Bearer ${token}`
//         }
//       });

//       const userPermissions = response.data;
//       setPermissions(userPermissions);

//       // Store permissions in localStorage for later use
//       localStorage.setItem('permissions', JSON.stringify(userPermissions));

//       console.log('Fetched and stored permissions:', userPermissions);
//     } catch (error) {
//       console.error('Error fetching permissions:', error);
//       setPermissions(undefined);
//     }
//   };

//   const login = (userToken, userPermissions) => {
//     localStorage.setItem('token', JSON.stringify(userToken));
//     setToken(userToken);

//     // Fetch permissions after login
//     fetchPermissions(userToken);
//   };

//   const logout = async () => {
//     try {
//       await AxiosInstance.post('/user/logout');
      
//       localStorage.removeItem('token');
//       localStorage.removeItem('permissions');

//       setToken(null);
//       setPermissions(undefined);

//       console.log('Logged out and cleared local storage.');
//     } catch (error) {
//       console.error('Logout error:', error);
//     }
//   };

//   return (
//     <AuthContext.Provider value={{ token, permissions, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };

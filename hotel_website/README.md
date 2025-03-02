# Hotel Website

## Overview
The **Hotel Website** is a Django-based web application that provides a complete hotel booking and management system. It includes features for user registration, booking management, notifications, inquiries, and real-time updates using WebSockets and Redis.

## Features
### 1. **User Authentication & Management**
- Custom user model using `AbstractUser`.
- User registration, login, logout.
- Profile management with fields such as bio, location, website, and profile picture.
- Role-based authentication (Guests, Receptionists, Managers).

### 2. **Hotel Room Booking System**
- Users can browse available rooms and make bookings.
- Booking details include check-in/check-out dates, room quantity, and total price calculation.
- Guests can manage their reservations.
- Managers and receptionists can view and manage all bookings.

### 3. **Notifications System**
- Managers and receptionists can send notifications to users.
- Users receive notifications in real time using WebSockets.
- Recent notifications are displayed in the dashboard.

### 4. **Inquiry System**
- Guests can send inquiries about room availability, pricing, etc.
- Admins and receptionists can respond to inquiries.
- Resolved inquiries are archived instead of being deleted.

### 5. **Real-Time Features with WebSockets & Redis**
- Real-time notifications using Django Channels and Redis.
- WebSockets handle instant updates for user notifications.

### 6. **Admin Dashboard**
- Overview of hotel activities (total bookings, inquiries, user statistics, etc.).
- Ability to manage user accounts, bookings, and inquiries.
- Notifications panel for sending announcements.

### 7. **Receptionist Dashboard**
- View and manage bookings.
- Respond to guest inquiries.
- Send notifications to users.

### 8. **Guest Dashboard**
- View booking history.
- Receive notifications.
- Send inquiries.

### 9. **Dynamic Home Page with Video Background**
- The homepage features a video background in a specific section.
- Users can explore the hotel features with an interactive UI.





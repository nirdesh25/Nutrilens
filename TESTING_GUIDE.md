# NutriLens AI - Testing Guide

Complete guide for testing all features of the application.

## Prerequisites

- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- PostgreSQL database configured

## Test Checklist

### ✅ 1. Authentication

**Register New User**
1. Go to `http://localhost:3000`
2. Click "Get Started"
3. Fill in registration form:
   - Name: Test User
   - Email: test@example.com
   - Password: password123
   - Age: 25 (optional)
4. Click "Create Account"
5. Should redirect to dashboard

**Login**
1. Logout if logged in
2. Go to login page
3. Enter credentials
4. Should redirect to dashboard

**Expected Results:**
- ✓ User created in database
- ✓ JWT token stored in localStorage
- ✓ Redirected to dashboard
- ✓ Can access protected routes

### ✅ 2. Dashboard

**View Dashboard**
1. Login and navigate to dashboard
2. Verify all module cards are visible:
   - Food Scanner
   - My Groceries
   - Health Profile
   - Waste Decisions
   - pH Strip Analysis
   - Smart Freshness Box
   - Analytics

**Expected Results:**
- ✓ All 7 modules displayed
- ✓ Stats cards show initial values (0)
- ✓ Navigation works
- ✓ Logout button functional

### ✅ 3. Food Scanner

**Scan Food Image**
1. Navigate to Food Scanner
2. Upload any food image (or use test image)
3. Click "Scan Food"
4. Wait for analysis

**Expected Results:**
- ✓ Image preview shown
- ✓ Loading state displayed
- ✓ Results show:
  - Food name
  - Freshness status (fresh/slightly_aged/rotten)
  - Risk score (0-100)
  - Confidence level
  - Recommendation
  - CO2 impact

**Test Cases:**
- Upload valid image → Success
- Upload non-image file → Error
- Upload very large file → Error or warning
- Scan multiple images → Each creates new result

### ✅ 4. Grocery Manager

**Add Grocery**
1. Navigate to My Groceries
2. Click "Add Grocery"
3. Fill form:
   - Food Name: Apple
   - Category: Fruit
   - Quantity: 5
   - Freshness: Fresh
4. Click "Save"

**Edit Grocery**
1. Click "Edit" on a grocery item
2. Change quantity to 3
3. Click "Save"

**Delete Grocery**
1. Click "Delete" on a grocery item
2. Confirm deletion

**Expected Results:**
- ✓ Grocery added to list
- ✓ Grocery updated successfully
- ✓ Grocery removed from list
- ✓ Empty state shown when no groceries

### ✅ 5. Health Profile

**Create Health Profile**
1. Navigate to Health Profile
2. Toggle health conditions:
   - Diabetes: ON
   - High BP: ON
   - Others: OFF
3. Click "Save Profile"

**View Recommendations**
1. After saving profile
2. Check recommendations section

**Expected Results:**
- ✓ Profile saved successfully
- ✓ Recommendations displayed:
  - Recommended foods (green)
  - Foods to avoid (red)
  - Meal suggestions
- ✓ Recommendations update based on conditions

**Test Cases:**
- No conditions selected → Generic recommendations
- Diabetes only → Low GI foods recommended
- Multiple conditions → Combined recommendations

### ✅ 6. Smart Freshness Box

**View Sensor Data**
1. Navigate to Smart Freshness Box
2. Observe sensor cards

**Expected Results:**
- ✓ 4 sensor cards displayed:
  - Temperature (°C)
  - Humidity (%)
  - Gas Level (PPM)
  - Light Level (%)
- ✓ Status indicators (normal/warning/critical)
- ✓ Alerts section shows recommendations
- ✓ Device status shows "Mock Data"
- ✓ Data refreshes every 10 seconds

**Test Scenarios:**
- Normal conditions → Green status
- High temperature → Warning/Critical status
- High gas levels → Alerts displayed

### ✅ 7. pH Strip Analysis

**Analyze pH Strip**
1. Navigate to pH Strip Analysis
2. Select food type (Milk/Juice/Meat/Other)
3. Upload pH strip image
4. Click "Analyze pH Strip"

**Expected Results:**
- ✓ pH value displayed (1-14)
- ✓ Safe range shown
- ✓ Spoilage status (fresh/questionable/spoiled)
- ✓ Confidence level
- ✓ Recommendation provided

**Test Cases:**
- Different food types → Different safe ranges
- Multiple analyses → Each creates new result

### ✅ 8. Analytics Dashboard

**View Analytics**
1. Navigate to Analytics
2. Observe metrics

**Expected Results:**
- ✓ Key metrics displayed:
  - Total CO2 saved
  - Total actions
  - Recent activity
- ✓ Actions breakdown chart
- ✓ Most wasted foods list
- ✓ Environmental impact summary

**Test Progression:**
1. Initial state → All zeros, empty state
2. After scanning food → Metrics update
3. After multiple actions → Charts populate

## API Testing

### Using FastAPI Docs

1. Go to `http://localhost:8000/docs`
2. Test each endpoint:

**Authentication**
```
POST /api/auth/register
POST /api/auth/login
```

**Food Scanner**
```
POST /api/scan/predict
GET /api/scan/history
GET /api/scan/waste-decision/{scan_id}
```

**Groceries**
```
GET /api/groceries
POST /api/groceries
PUT /api/groceries/{id}
DELETE /api/groceries/{id}
```

**Health**
```
POST /api/health/profile
GET /api/health/profile
PUT /api/health/profile
GET /api/health/recommendations
```

**Waste**
```
POST /api/waste/log
GET /api/waste/logs
GET /api/waste/analytics
```

**Sensor (Smart Box)**
```
GET /api/sensor/current
GET /api/sensor/history?hours=24
GET /api/sensor/status
POST /api/sensor/ingest
```

**pH Analysis**
```
POST /api/ph/analyze
GET /api/ph/food-types
```

### Using cURL

**Register User**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

**Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Get Groceries (with token)**
```bash
curl -X GET http://localhost:8000/api/groceries \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Testing

**Check Tables Created**
```sql
\dt  -- List all tables

-- Should see:
-- users
-- groceries
-- scan_results
-- waste_logs
-- health_profiles
-- sensor_data
```

**Verify Data**
```sql
SELECT * FROM users;
SELECT * FROM groceries;
SELECT * FROM scan_results;
SELECT * FROM waste_logs;
SELECT * FROM health_profiles;
SELECT * FROM sensor_data;
```

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install ab  # Mac

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

### Response Time
- API endpoints should respond < 200ms
- Image upload/scan < 2s (with mock data)
- Page load < 1s

## Security Testing

**Authentication**
- ✓ Cannot access protected routes without token
- ✓ Invalid token returns 401
- ✓ Expired token returns 401

**Authorization**
- ✓ Users can only access their own data
- ✓ Cannot modify other users' groceries
- ✓ Cannot view other users' health profiles

**Input Validation**
- ✓ SQL injection prevented
- ✓ XSS attacks blocked
- ✓ File upload validation works
- ✓ Email format validated
- ✓ Password requirements enforced

## Browser Testing

Test on multiple browsers:
- ✓ Chrome/Edge (Chromium)
- ✓ Firefox
- ✓ Safari (Mac)

Test responsive design:
- ✓ Desktop (1920x1080)
- ✓ Tablet (768x1024)
- ✓ Mobile (375x667)

## Error Handling

**Test Error Scenarios:**
1. Backend offline → Show error message
2. Invalid credentials → Show error
3. Network timeout → Show error
4. Invalid file upload → Show error
5. Database connection lost → Graceful degradation

## Integration Testing

**Complete User Flow:**
1. Register new account
2. Login
3. Create health profile
4. Add groceries
5. Scan food image
6. View recommendations
7. Check analytics
8. Monitor Smart Box
9. Analyze pH strip
10. Logout

**Expected:** All steps complete without errors

## Mock Data Verification

**Verify Mock Responses:**
- Food scanner returns random but valid data
- Sensor data within realistic ranges
- pH analysis returns appropriate values
- Health recommendations are logical

## Deployment Testing

**Pre-Deployment Checklist:**
- [ ] All tests pass locally
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Static files build successfully
- [ ] API documentation accessible
- [ ] CORS configured correctly
- [ ] HTTPS enabled (production)
- [ ] Error logging configured

## Known Limitations (Mock Data)

1. **Food Scanner:** Returns random predictions (not real AI)
2. **Smart Freshness Box:** Shows mock sensor data
3. **pH Analysis:** Returns random pH values
4. **Food Recognition:** Limited to predefined foods

These will be replaced with real models after training.

## Troubleshooting

**Backend won't start:**
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check port 8000 is available

**Frontend won't start:**
- Check NEXT_PUBLIC_API_URL in .env.local
- Verify Node.js version (18+)
- Delete node_modules and reinstall

**API returns 401:**
- Check token in localStorage
- Token may be expired (login again)
- Verify Authorization header format

**Database errors:**
- Run init_db.py to create tables
- Check database connection string
- Verify PostgreSQL user permissions

## Success Criteria

Application is ready for deployment when:
- ✅ All authentication flows work
- ✅ All CRUD operations successful
- ✅ All pages load without errors
- ✅ Mock data displays correctly
- ✅ Responsive design works
- ✅ API documentation accessible
- ✅ Error handling graceful
- ✅ Security measures in place

## Next Steps After Testing

1. Train real AI models with datasets
2. Replace mock data with real predictions
3. Connect IoT hardware to Smart Box
4. Collect pH strip images for training
5. Deploy to production
6. Monitor and optimize performance

---

**Happy Testing!** 🧪

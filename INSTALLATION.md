# Installation Guide - Farm Management App

This guide will walk you through the complete installation process of the Farm Management App for ERPNext.

## Prerequisites

Before installing the Farm Management App, ensure you have:

### System Requirements
- **Operating System**: Ubuntu 18.04+ / CentOS 7+ / macOS 10.14+
- **Python**: 3.6 or higher
- **Node.js**: 14.x or higher
- **Database**: MariaDB 10.3+ or MySQL 8.0+
- **ERPNext**: Version 13.0 or higher

### ERPNext Installation
If you don't have ERPNext installed, follow the official installation guide:
- [ERPNext Installation Guide](https://github.com/frappe/bench#installation)

## Installation Methods

### Method 1: Using Bench (Recommended)

#### Step 1: Navigate to Bench Directory
```bash
cd /path/to/your/bench
# Example: cd /home/frappe/frappe-bench
```

#### Step 2: Get the App
```bash
bench get-app https://github.com/yourusername/farm_management.git
```

#### Step 3: Install on Site
```bash
bench --site your-site-name install-app farm_management
```

#### Step 4: Migrate Database
```bash
bench --site your-site-name migrate
```

#### Step 5: Restart Services
```bash
bench restart
```

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
cd /path/to/your/bench/apps
git clone https://github.com/yourusername/farm_management.git
```

#### Step 2: Install Dependencies
```bash
cd farm_management
pip install -r requirements.txt
```

#### Step 3: Install App
```bash
cd /path/to/your/bench
bench --site your-site-name install-app farm_management
```

#### Step 4: Complete Installation
```bash
bench --site your-site-name migrate
bench restart
```

## Post-Installation Setup

### 1. User Roles Configuration

Create the following roles in your ERPNext system:

#### Farm Manager Role
```bash
bench --site your-site-name execute "
from frappe import get_doc
role = get_doc({
    'doctype': 'Role',
    'role_name': 'Farm Manager',
    'desk_access': 1
})
role.insert()
"
```

#### Farm Worker Role
```bash
bench --site your-site-name execute "
from frappe import get_doc
role = get_doc({
    'doctype': 'Role',
    'role_name': 'Farm Worker',
    'desk_access': 1
})
role.insert()
"
```

### 2. Initial Data Setup

#### Create Your First Farm
1. Login to ERPNext
2. Go to **Farm Management > Farm**
3. Click **New**
4. Fill in your farm details:
   - Farm Name
   - Farm Type (Poultry/Pig/Mixed)
   - Location details
   - Contact information

#### Setup Feed Types
1. Go to **Farm Management > Feed Type**
2. Create feed types for your animals:
   - **Poultry Starter**: High protein feed for chicks
   - **Poultry Layer**: Feed for laying hens
   - **Pig Grower**: Feed for growing pigs
   - **Pig Finisher**: Feed for finishing pigs

### 3. User Permissions

Assign appropriate roles to users:

```bash
# Add Farm Manager role to a user
bench --site your-site-name execute "
import frappe
user = frappe.get_doc('User', 'manager@yourfarm.com')
user.add_roles('Farm Manager')
user.save()
"

# Add Farm Worker role to a user
bench --site your-site-name execute "
import frappe
user = frappe.get_doc('User', 'worker@yourfarm.com')
user.add_roles('Farm Worker')
user.save()
"
```

## Configuration

### 1. System Settings

#### Enable Required Modules
1. Go to **Setup > Module Settings**
2. Enable the **Farm Management** module
3. Configure module permissions as needed

#### Setup Number Series
The app uses the following number series:
- **Farm**: FM-.YYYY.-.#####
- **Poultry Batch**: PB-.YYYY.-.#####
- **Pig**: Individual pig IDs
- **Health Record**: HR-.YYYY.-.MM.-.#####
- **Feed Record**: FR-.YYYY.-.MM.-.#####

### 2. Customization Options

#### Custom Fields
Add custom fields specific to your farm:

```python
# Example: Add custom field for pig breed certification
custom_field = {
    "doctype": "Custom Field",
    "dt": "Pig",
    "fieldname": "breed_certification",
    "fieldtype": "Data",
    "label": "Breed Certification",
    "insert_after": "breed"
}
```

#### Custom Reports
Create custom reports for your specific needs:
1. Go to **Build > Report Builder**
2. Select the relevant DocType
3. Configure fields and filters
4. Save and share with appropriate roles

### 3. Integration Setup

#### Email Configuration
Configure email for notifications:
1. Go to **Setup > Email > Email Account**
2. Setup your email account
3. Configure notification templates

#### Print Formats
Customize print formats for:
- Health certificates
- Feed consumption reports
- Production summaries
- Breeding records

## Verification

### Test Installation
1. **Login Test**: Ensure you can login with appropriate roles
2. **Create Test Records**: 
   - Create a test farm
   - Add a poultry batch or pig
   - Record some health and feed data
3. **Generate Reports**: Test basic reporting functionality

### Performance Check
```bash
# Check app status
bench --site your-site-name console

# In the console:
import frappe
print(frappe.get_installed_apps())
# Should include 'farm_management'
```

## Troubleshooting

### Common Issues

#### 1. App Not Showing in Modules
**Solution**: Clear cache and restart
```bash
bench --site your-site-name clear-cache
bench restart
```

#### 2. Permission Errors
**Solution**: Check role assignments
```bash
bench --site your-site-name execute "
import frappe
print(frappe.get_roles('your-username'))
"
```

#### 3. Database Migration Errors
**Solution**: Run migration manually
```bash
bench --site your-site-name migrate --skip-failing
```

#### 4. Import Errors
**Solution**: Check Python path and dependencies
```bash
bench --site your-site-name console
# Test imports:
import farm_management
```

### Log Files
Check these log files for detailed error information:
- `/path/to/bench/logs/web.error.log`
- `/path/to/bench/logs/worker.error.log`
- `/path/to/bench/logs/schedule.log`

### Getting Help

1. **Check Documentation**: Review the README.md file
2. **Community Support**: Post on ERPNext Community Forum
3. **GitHub Issues**: Report bugs on the GitHub repository
4. **Professional Support**: Contact for custom development needs

## Backup and Maintenance

### Regular Backups
```bash
# Create backup
bench --site your-site-name backup

# Backup with files
bench --site your-site-name backup --with-files
```

### Updates
```bash
# Update the app
bench get-app farm_management --branch main
bench --site your-site-name migrate
bench restart
```

### Monitoring
Set up monitoring for:
- Database performance
- Application logs
- User activity
- System resources

## Security Considerations

1. **User Access**: Regularly review user permissions
2. **Data Backup**: Implement automated backup strategy
3. **SSL Certificate**: Ensure HTTPS is enabled
4. **Database Security**: Secure database access
5. **Regular Updates**: Keep ERPNext and the app updated

## Next Steps

After successful installation:

1. **Training**: Train your team on using the system
2. **Data Migration**: Import existing farm data if applicable
3. **Customization**: Implement farm-specific customizations
4. **Integration**: Connect with other systems if needed
5. **Monitoring**: Set up performance monitoring

---

**Need Help?** Contact support or check the documentation for more detailed information.


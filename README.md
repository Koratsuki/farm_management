# Farm Management App for ERPNext

A comprehensive farm management application for ERPNext, specifically designed for poultry and pig farming operations.

## Features

### 🏭 Farm Management
- **Farm Registration**: Complete farm information including location, certifications, and contact details
- **Multi-farm Support**: Manage multiple farms from a single system
- **Farm Analytics**: Track performance metrics across all farms

### 🐔 Poultry Management
- **Batch Tracking**: Manage poultry in batches with breed, age, and population tracking
- **Egg Production**: Daily egg collection records with quality metrics
- **Production Analytics**: Track laying rates, egg quality, and batch performance
- **Mortality Tracking**: Monitor and analyze mortality rates

### 🐷 Pig Management
- **Individual Pig Tracking**: Complete lifecycle management from birth to market
- **Breeding Management**: Track breeding cycles, pregnancy, and farrowing
- **Weight Monitoring**: Regular weight tracking with growth analysis
- **Genealogy Tracking**: Maintain breeding records and family trees

### 🏥 Health Management
- **Health Records**: Comprehensive health tracking for all animals
- **Vaccination Schedules**: Track vaccinations and preventive care
- **Treatment Records**: Document treatments, medications, and recovery
- **Veterinary Integration**: Track veterinary visits and costs

### 🌾 Feed Management
- **Feed Types**: Manage different feed formulations and nutritional content
- **Feed Records**: Track daily feeding with consumption analysis
- **Cost Tracking**: Monitor feed costs and conversion ratios
- **Inventory Management**: Track feed stock levels and reorder points

### 📊 Analytics & Reporting
- **Performance Metrics**: Growth rates, production efficiency, and profitability
- **Cost Analysis**: Feed conversion ratios and cost per unit production
- **Health Analytics**: Disease patterns and treatment effectiveness
- **Production Forecasting**: Predict production based on historical data

## Installation

### Prerequisites
- ERPNext v13.0 or higher
- Python 3.6+
- MariaDB/MySQL

### Installation Steps

1. **Navigate to your ERPNext bench directory:**
   ```bash
   cd /path/to/your/bench
   ```

2. **Get the app:**
   ```bash
   bench get-app https://github.com/yourusername/farm_management.git
   ```

3. **Install the app on your site:**
   ```bash
   bench --site your-site-name install-app farm_management
   ```

4. **Migrate the database:**
   ```bash
   bench --site your-site-name migrate
   ```

5. **Restart the bench:**
   ```bash
   bench restart
   ```

## Configuration

### Initial Setup

1. **Create User Roles:**
   - Farm Manager: Full access to all farm operations
   - Farm Worker: Limited access for daily operations
   - Veterinarian: Access to health records and treatments

2. **Setup Farms:**
   - Navigate to Farm Management > Farm
   - Create your farm records with complete information

3. **Configure Feed Types:**
   - Set up your feed formulations with nutritional information
   - Configure cost and stock management parameters

### Permissions

The app comes with predefined role-based permissions:

- **System Manager**: Full administrative access
- **Farm Manager**: Complete farm operations management
- **Farm Worker**: Daily operations (feeding, health checks, data entry)
- **Veterinarian**: Health records and treatment management

## Usage

### Daily Operations

1. **Morning Routine:**
   - Record egg collection (Poultry)
   - Update health status
   - Record feeding

2. **Health Monitoring:**
   - Daily health checks
   - Record any symptoms or treatments
   - Update vaccination schedules

3. **Weight Tracking:**
   - Regular weight measurements for pigs
   - Growth rate analysis
   - Market readiness assessment

### Breeding Management

1. **Breeding Records:**
   - Record breeding events
   - Track pregnancy progress
   - Document farrowing results

2. **Offspring Management:**
   - Automatic piglet record creation
   - Genealogy tracking
   - Performance monitoring

### Analytics

1. **Production Reports:**
   - Daily/weekly/monthly production summaries
   - Efficiency metrics and trends
   - Cost analysis reports

2. **Health Analytics:**
   - Disease pattern analysis
   - Treatment effectiveness
   - Mortality rate tracking

## DocTypes Overview

### Core DocTypes
- **Farm**: Main farm information and configuration
- **Animal**: Generic animal tracking (base class)

### Poultry Management
- **Poultry Batch**: Batch-based poultry management
- **Egg Production Record**: Daily egg collection tracking

### Pig Management
- **Pig**: Individual pig lifecycle management
- **Breeding Record**: Breeding and farrowing tracking
- **Weight Record**: Growth monitoring and analysis

### Health & Feed Management
- **Health Record**: Universal health tracking system
- **Feed Type**: Feed formulations and specifications
- **Feed Record**: Daily feeding and consumption tracking

## API Integration

The app provides REST API endpoints for:
- Mobile app integration
- IoT device data collection
- Third-party system integration
- Automated data import/export

## Customization

### Adding Custom Fields
```python
# Example: Adding custom field to Pig DocType
frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Pig",
    "fieldname": "custom_field_name",
    "fieldtype": "Data",
    "label": "Custom Field Label"
}).insert()
```

### Custom Reports
Create custom reports using ERPNext's Report Builder or by creating custom Python reports in the `reports` directory.

## Support

### Documentation
- [ERPNext Documentation](https://docs.erpnext.com/)
- [Frappe Framework Documentation](https://frappeframework.com/docs)

### Community
- [ERPNext Community Forum](https://discuss.erpnext.com/)
- [GitHub Issues](https://github.com/yourusername/farm_management/issues)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/farm_management.git

# Create a new site for development
bench new-site farm-dev.local

# Install the app
bench --site farm-dev.local install-app farm_management

# Start development server
bench start
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.1.0
- Initial release
- Basic farm, poultry, and pig management
- Health and feed tracking
- Core reporting functionality

## Roadmap

### Version 0.2.0
- Mobile app support
- IoT integration
- Advanced analytics dashboard
- Automated alerts and notifications

### Version 0.3.0
- Financial management integration
- Supply chain management
- Advanced breeding algorithms
- Machine learning predictions

## Screenshots

[Add screenshots of the application interface here]

## Support the Project

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code
- 📖 Improving documentation

---

**Made with ❤️ for the farming community**


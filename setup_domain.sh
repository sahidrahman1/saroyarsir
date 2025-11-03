#!/bin/bash
# Setup nginx for gsteaching.com domain

echo "🌐 Setting up nginx for gsteaching.com..."
echo "=========================================="

# Copy nginx config
sudo cp nginx_gsteaching.conf /etc/nginx/sites-available/gsteaching.com

# Remove old symlink if exists
sudo rm -f /etc/nginx/sites-enabled/gsteaching.com
sudo rm -f /etc/nginx/sites-enabled/saroyarsir

# Create symlink
sudo ln -s /etc/nginx/sites-available/gsteaching.com /etc/nginx/sites-enabled/

# Test nginx configuration
echo ""
echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Check if certbot is installed
    if command -v certbot &> /dev/null; then
        echo ""
        echo "🔒 Getting SSL certificate..."
        sudo certbot --nginx -d gsteaching.com -d www.gsteaching.com --non-interactive --agree-tos --redirect
        
        if [ $? -eq 0 ]; then
            echo "✅ SSL certificate obtained successfully"
        else
            echo "⚠️  SSL certificate failed. You can run manually:"
            echo "   sudo certbot --nginx -d gsteaching.com -d www.gsteaching.com"
        fi
    else
        echo "⚠️  Certbot not installed. Install it first:"
        echo "   sudo apt install certbot python3-certbot-nginx"
        echo ""
        echo "📝 For now, commenting out SSL lines in nginx config..."
        sudo sed -i 's/ssl_certificate/#ssl_certificate/g' /etc/nginx/sites-available/gsteaching.com
        sudo sed -i 's/listen 443/#listen 443/g' /etc/nginx/sites-available/gsteaching.com
        sudo sed -i 's/return 301 https/#return 301 https/g' /etc/nginx/sites-available/gsteaching.com
    fi
    
    # Reload nginx
    echo ""
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "=========================================="
    echo "✅ Domain setup complete!"
    echo ""
    echo "🌐 Your site is now accessible at:"
    echo "   http://gsteaching.com"
    echo "   http://www.gsteaching.com"
    echo ""
    echo "📝 Make sure your DNS is configured:"
    echo "   A Record: gsteaching.com → YOUR_SERVER_IP"
    echo "   A Record: www.gsteaching.com → YOUR_SERVER_IP"
    echo ""
    echo "🔒 To get SSL certificate manually (if not done):"
    echo "   sudo certbot --nginx -d gsteaching.com -d www.gsteaching.com"
else
    echo "❌ Nginx configuration has errors. Please fix them."
    exit 1
fi

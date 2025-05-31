require('dotenv').config();
const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware setup
app.use(cors()); // Allow cross-origin requests
app.use(bodyParser.json()); // Parse JSON bodies

// POST endpoint to handle contact form submissions
app.post('/api/contact', async (req, res) => {
    // Destructure form fields from request body
    const { name, email, message } = req.body;

    // Basic validation
    if (!name || !email || !message) {
        return res.status(400).json({ error: 'All fields are required.' });
    }

    // Configure Nodemailer transporter (use your real email credentials here)
    const transporter = nodemailer.createTransport({
        service: 'gmail', // e.g., 'gmail'
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASS
        }
    });

    // Email options
    const mailOptions = {
        from: email,
        to: 'wandeusamuel506@gmail.com', // where you want to receive messages
        subject: `New Contact Form Submission from ${name}`,
        text: `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`
    };

    try {
        // Send the email
        await transporter.sendMail(mailOptions);
        res.status(200).json({ message: 'Message sent successfully!' });
    } catch (error) {
        // Log and return error if sending fails
        console.error('Error sending email:', error);
        res.status(500).json({ error: 'Failed to send message. Please try again later.' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
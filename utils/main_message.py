def get_verified_html(username:str):
  html_message = """\
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Welcome to Our Library</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          background-color: #f0f0f0; /* Default background color, replace with user's preference */
        }}
        .header {{
          background-color: #004d99; /* Default header color, replace with user's preference */
          color: #ffffff;
          padding: 20px;
          text-align: center;
        }}
        .content {{
          padding: 20px;
          text-align: center;
        }}
        .library-image {{
          width: 100%;
          max-width: 600px;
          display: block;
          margin: 20px auto;
        }}
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Welcome to Our Library Management System</h1>
      </div>

      <div class="content">
        <h2>Dear {username} Your Account Verified Sucesfully </h2>
        <p>
          Hello and welcome! We're thrilled to have you join our community of book
          lovers and knowledge seekers. Our library is your gateway to a vast
          world of literature, learning, and leisure.
        </p>

        <img src="https://rohanpudasaini.com.np/wp-content/uploads/2024/04/lms_logo1.png" alt="Library Image" class="library-image" />
        <!-- Replace "library-image.jpg" with the actual image path -->

        <p>
          Feel free to explore our collections, participate in our events, and
          take advantage of all the resources available to you. If you have any
          questions or need assistance, our staff is always here to help.
        </p>

        <p>Happy reading!</p>
      </div>
    </body>
  </html>


  """
  return html_message.format(username=username)

def get_return_reminder_html(username:str, name:str, object:str):
    html_message = """\
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Return Reminder</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
          }}
          .header {{
            background-color: #f44336; /* Alert color */
            color: #ffffff;
            padding: 20px;
            text-align: center;
          }}
          .content {{
            padding: 20px;
            text-align: center;
          }}
          .library-image {{
            width: 100%;
            max-width: 600px;
            display: block;
            margin: 20px auto;
          }}
        </style>
      </head>
      <body>
        <div class="header">
          <h1>{object} Return Reminder</h1>
        </div>

        <div class="content">
          <h2>Dear {username},</h2>
          <p>
            This is a friendly reminder that your borrowed {object} <strong>"{name}"</strong> is due for return in 3 days. 
          </p>

          <img src="https://rohanpudasaini.com.np/wp-content/uploads/2024/04/lms_logo1.png" alt="Library Image" class="library-image" />
          <!-- Replace "library-image.jpg" with the actual image path -->

          <p>
            Please make sure to return it on time to avoid any late fees and to help keep our library system efficient for all users.
          </p>
          <p>
            If you have already returned the {object} or need an extension, please disregard this message or contact our staff for assistance.
          </p>
          <p>Thank you for being a valued member of our library community!</p>
        </div>
      </body>
    </html>
    """

    return html_message.format(object=object,username=username, name=name)
  

def get_expiry_notification_html(username:str, name:str, object:str, expiry_date:str, fine_amount:str):
    html_message = """\
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Expiry Notification</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
          }}
          .header {{
            background-color: #d32f2f; /* Notification color */
            color: #ffffff;
            padding: 20px;
            text-align: center;
          }}
          .content {{
            padding: 20px;
            text-align: center;
          }}
          .library-image {{
            width: 100%;
            max-width: 600px;
            display: block;
            margin: 20px auto;
          }}
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Expiry Notification</h1>
        </div>

        <div class="content">
          <h2>Dear {username},</h2>
          <p>
            We hope this message finds you well. This is to inform you that the borrowing period for your {object} <strong>"{name}"</strong> has expired on <strong>{expiry_date}</strong>.
          </p>

          <img src="https://rohanpudasaini.com.np/wp-content/uploads/2024/04/lms_logo1.png" alt="Library Image" class="library-image" />

          <p>
            As of now, a late return fine of <strong>रु {fine_amount}</strong> has been incurred. We kindly request that you return the {object} as soon as possible to minimize any additional charges.
          </p>
          <p>
            Please visit our library or contact our staff for assistance in returning the {object} or if you have any questions regarding your fine.
          </p>
          <p>Thank you for your prompt attention to this matter.</p>
        </div>
      </body>
    </html>
    """

    return html_message.format(username=username, name=name, object=object,expiry_date=expiry_date, fine_amount=fine_amount)

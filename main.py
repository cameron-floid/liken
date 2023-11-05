import instaloader
from instaloader.exceptions import ProfileNotExistsException, LoginRequiredException, BadCredentialsException, \
    TwoFactorAuthRequiredException
import os


# Function to ensure a directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(current_directory, 'data')

# Initialize the Instaloader instance
loader = instaloader.Instaloader()


def login(username, password):
    """Log into Instagram with the provided username and password."""
    try:
        loader.login(username, password)
        return True
    except BadCredentialsException:
        print("Error: The username or password is incorrect.")
    except TwoFactorAuthRequiredException:
        print("Error: Two-factor authentication is required. This script does not support 2FA.")
    except Exception as e:
        print(f"An error occurred during login: {e}")
    return False


def download_profile_posts(username):
    """Downloads the specified user's posts."""
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except ProfileNotExistsException:
        print(f"The profile for username '{username}' does not exist.")
        return

    # Create a directory for the user's posts
    user_posts_directory = os.path.join(data_directory, username, 'posts')
    ensure_directory_exists(user_posts_directory)

    # Download each post into its own directory based on the post ID
    for post in profile.get_posts():
        post_directory = os.path.join(user_posts_directory, post.shortcode)
        ensure_directory_exists(post_directory)
        loader.dirname_pattern = post_directory
        loader.download_post(post, target=profile.username)


def download_profile_follow_list(username, follow_type):
    """Downloads the specified user's followers or followees list."""
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except ProfileNotExistsException:
        print(f"The profile for username '{username}' does not exist.")
        return
    except LoginRequiredException:
        print("Error: You need to be logged in to access this information.")
        return

    # Directory for followers/followees list
    follow_list_directory = os.path.join(data_directory, username, follow_type)
    ensure_directory_exists(follow_list_directory)

    # File for saving the follow list
    follow_list_file = os.path.join(follow_list_directory, f"{follow_type}.txt")

    follow_list = profile.get_followers() if follow_type == 'followers' else profile.get_followees()
    with open(follow_list_file, "w") as f:
        for follow in follow_list:
            f.write(f"{follow.username}\n")


def download_profile_stories(username):
    """Downloads the specified user's stories."""
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except ProfileNotExistsException:
        print(f"The profile for username '{username}' does not exist.")
        return
    except LoginRequiredException:
        print("Error: You need to be logged in to access stories.")
        return

    # Create a directory for the user's stories
    user_stories_directory = os.path.join(data_directory, username, 'stories')
    ensure_directory_exists(user_stories_directory)

    # Checking if the profile has stories and downloading them
    if profile.has_public_story:
        loader.download_stories(userids=[profile.userid], filename_target=user_stories_directory)


def main_menu():
    """Displays the main menu and handles user input."""
    print("Welcome to the Instaloader Menu!")
    my_username = input("Please enter your Instagram username for login: ")
    my_password = input("Please enter your Instagram password: ")

    if not login(my_username, my_password):
        return  # Exit if login failed

    while True:
        print("\nInstaloader Menu:")
        print("1. Download Profile Posts")
        print("2. Download Profile Stories")  # Placeholder for stories functionality
        print("3. Download Profile Followers List")
        print("4. Download Profile Followees List")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "5":
            print("Exiting program.")
            break

        username = input("Enter the Instagram username: ")

        if choice == "1":
            download_profile_posts(username)
        elif choice == "2":
            download_profile_stories(username)
        elif choice == "3":
            download_profile_follow_list(username, 'followers')
        elif choice == "4":
            download_profile_follow_list(username, 'followees')
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()

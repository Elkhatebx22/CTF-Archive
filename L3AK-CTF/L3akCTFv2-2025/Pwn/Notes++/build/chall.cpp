#include <iostream>
#include <vector>
#include <memory>
#include <limits>
#include <algorithm>
#include <ctime>
#include <string_view>


class Note {
public:
    virtual ~Note() {}

    // Default implementation prints a message
    virtual void displayContent() const {
        std::cout << "[Note] displayContent() not implemented.\n";
    }

    // Default implementation prints a message
    virtual void setContent() {
        std::cout << "[Note] setContent() not implemented.\n";
    }
};

class RandomNote : public Note {
private:
    std::string_view content;

    static std::string_view getRandomPhrase() {
        static constexpr std::string_view phrases[] = {
            "The quick brown fox jumps over the lazy dog.",
            "Lorem ipsum dolor sit amet.",
            "Remember to buy milk tomorrow.",
            "Meeting rescheduled to 3 PM.",
            "Your package has been shipped.",
            "Don't forget to call Alice.",
            "Backup your data regularly.",
            "Coffee break at 10:30 AM.",
            "Finish the report by Friday.",
            "Update your software soon."
        };

        constexpr size_t phraseCount = sizeof(phrases) / sizeof(phrases[0]);
        int idx = std::rand() % phraseCount;
        return phrases[idx];
    }

public:
    void setContent() override {
        content = getRandomPhrase(); // No allocation — just a view
    }

    void displayContent() const override {
        if (!content.empty())
            std::cout << "Note content: " << content << "\n";
        else
            std::cout << "(Note is empty)\n";
    }
};

class FixedNote : public Note {
private:
    std::array<char, 40> buffer;

public:
    FixedNote() {}

    void setContent() override {
        std::cout << "Enter note: ";
        std::string input;
        std::getline(std::cin, input);

        std::size_t len = std::min(input.size(), buffer.size());
        std::copy_n(input.begin(), len, buffer.begin());
    }

    void displayContent() const override {
        std::cout << "Note content: " << buffer.data() << "\n";
    }
};

class DynamicNote : public Note {
private:
    std::string buffer;

public:
    void setContent() override {
        std::cout << "Enter note: ";
        std::getline(std::cin, buffer);
    }

    void displayContent() const override {
        std::cout << "Note content: " << buffer << "\n";
    }
};

void printMainMenu() {
    std::cout << "\n=== Note Manager ===\n";
    std::cout << "1. Create note\n";
    std::cout << "2. List notes\n";
    std::cout << "3. Set note content\n";
    std::cout << "4. Display note content\n";
    std::cout << "5. Delete note\n";
    std::cout << "6. Exit\n";
    std::cout << "Enter your choice: ";
}

void printSubMenu() {
    std::cout << "\n--- Select Note Type ---\n";
    std::cout << "1. RandomNote\n";
    std::cout << "2. FixedNote\n";
    std::cout << "3. DynamicNote\n";
    std::cout << "Enter your choice: ";
}

int main() {
    std::vector<Note *> notes;
    int choice = 0;

    while (true) {
        printMainMenu();
        std::cin >> choice;
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        if (choice == 1) {
            int typeChoice = 0;
            printSubMenu();
            std::cin >> typeChoice;
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

            switch (typeChoice) {
                case 1:
                    notes.push_back(new RandomNote());
                    std::cout << "RandomNote created.\n";
                    break;
                case 2:
                    notes.push_back(new FixedNote());
                    std::cout << "FixedNote created.\n";
                    break;
                case 3:
                    notes.push_back(new DynamicNote());
                    std::cout << "DynamicNote created.\n";
                    break;
                default:
                    std::cout << "Invalid note type.\n";
                    break;
            }
        } else if (choice == 2) {
            if (notes.empty()) {
                std::cout << "No notes available.\n";
                continue;
            }
            std::cout << "--- Notes List ---\n";
            for (size_t i = 0; i < notes.size(); ++i) {
                std::cout << i << ": ";
                notes[i]->displayContent();
            }
        } else if (choice == 3) {
            int index;
            std::cout << "Enter note index to set content: ";
            std::cin >> index;
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

            if (index < std::ssize(notes)) {
                notes[index]->setContent();
            } else {
                std::cout << "Invalid index.\n";
            }
        } else if (choice == 4) {
            int index;
            std::cout << "Enter note index to display content: ";
            std::cin >> index;
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

            if (index < std::ssize(notes)) {
                notes[index]->displayContent();
            } else {
                std::cout << "Invalid index.\n";
            }
        } else if (choice == 5) {
            int index;
            std::cout << "Enter note index to delete: ";
            std::cin >> index;
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

            if (index < std::ssize(notes)) {
                delete notes[index];
                notes.erase(notes.begin() + index); // deletes and frees memory
                std::cout << "Note " << index << " deleted.\n";
            } else {
                std::cout << "Invalid index.\n";
            }
        } else if (choice == 6) {
            std::cout << "Goodbye!\n";
            break;
        } else {
            std::cout << "Invalid choice. Try again.\n";
        }
    }

    return 0;
}
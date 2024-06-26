import torch.nn as nn
import pickle
import matplotlib.pyplot as plt
from torchvision.transforms import v2
import torch.utils.data as data_utils
from files.data import (
    read_words_generate_csv,
    read_bbox_csv_show_image,
    get_dataloaders,
    dataloader_show,
    read_maps,
)
from files.dataset import CustomObjectDetectionDataset
from files.transform import ResizeWithPad
import torch
from files.model import CRNN, visualize_model, visualize_featuremap, CRNN_lstm, CRNN_rnn
from files.test_train import train, test
from files.functions import generated_data_dir, htr_ds_dir
from wakepy import keep

# Todo confusion matrix

device = "cuda" if torch.cuda.is_available() else "cpu"
image_transform = v2.Compose([ResizeWithPad(h=32, w=110), v2.Grayscale()])
do = 1
text_label_max_length = 6
model = 2
torch.manual_seed(1)

if do == 1:
    with keep.running() as k:
        print("htr training and testing")
        read_words_generate_csv()

        char_to_int_map, int_to_char_map, char_set = read_maps()
        print("char_set", char_set)
        # char_to_int_map['_'] = '15'
        # int_to_char_map['15'] = '_'
        int_to_char_map["16"] = ""

        trl, tl = get_dataloaders(
            image_transform,
            char_to_int_map,
            int_to_char_map,
            800,
            text_label_max_length,
            char_set,
        )

        dataloader_show(trl, number_of_images=2, int_to_char_map=int_to_char_map)

        BLANK_LABEL = 15

        if model == 2:
            crnn = CRNN().to(device)
        elif model == 3:
            crnn = CRNN_lstm().to(device)
        elif model == 1:
            crnn = CRNN_rnn().to(device)

        criterion = nn.CTCLoss(blank=BLANK_LABEL, reduction="mean", zero_infinity=True)
        optimizer = torch.optim.Adam(crnn.parameters(), lr=0.001)

        MAX_EPOCHS = 2500
        list_training_loss = []
        list_testing_loss = []
        list_testing_wer = []
        list_testing_cer = []

        for epoch in range(MAX_EPOCHS):
            training_loss = train(
                trl, crnn, optimizer, criterion, BLANK_LABEL, text_label_max_length
            )
            testing_loss, wer, cer = test(
                int_to_char_map,
                tl,
                crnn,
                optimizer,
                criterion,
                BLANK_LABEL,
                text_label_max_length,
            )

            list_training_loss.append(training_loss)
            list_testing_loss.append(testing_loss)
            list_testing_wer.append(wer)
            list_testing_cer.append(cer)

            prefix = ""
            if model == 2:
                prefix = "gru_"
            elif model == 3:
                prefix = "lstm_"
            elif model == 1:
                prefix = "rnn_"

            if epoch == 4:
                print("training loss", list_training_loss)
                with open(generated_data_dir() + "list_training_loss.pkl", "wb") as f1:
                    pickle.dump(list_training_loss, f1)
                print("testing loss", list_testing_loss)
                with open(generated_data_dir() + "list_testing_loss.pkl", "wb") as f2:
                    pickle.dump(list_testing_loss, f2)
                with open(
                    generated_data_dir() + prefix + "list_testing_wer.pkl", "wb"
                ) as f3:
                    pickle.dump(list_testing_wer, f3)
                with open(
                    generated_data_dir() + prefix + "list_testing_cer.pkl", "wb"
                ) as f4:
                    pickle.dump(list_testing_cer, f4)
                break

        torch.save(crnn.state_dict(), generated_data_dir() + "trained_reader")


if do == 2:
    print("visualize featuremap")
    char_to_int_map, int_to_char_map, char_set = read_maps()
    crnn = CRNN().to(device)
    crnn.load_state_dict(torch.load(generated_data_dir() + "trained_reader"))
    trl, _ = get_dataloaders(
        image_transform,
        char_to_int_map,
        int_to_char_map,
        5,
        text_label_max_length,
        char_set,
    )
    visualize_featuremap(crnn, trl, 1)

if do == 3:
    print("visualize model")
    char_to_int_map, int_to_char_map, char_set = read_maps()
    crnn = CRNN().to(device)
    crnn.load_state_dict(torch.load(generated_data_dir() + "trained_reader"))
    trl, tl = get_dataloaders(
        image_transform,
        char_to_int_map,
        int_to_char_map,
        5,
        text_label_max_length,
        char_set,
    )
    visualize_model(trl, crnn)


if do == 45:
    annotations_file = htr_ds_dir() + "train/" + "_annotations.csv"
    image_folder = htr_ds_dir() + "train/"

    ds = CustomObjectDetectionDataset(annotations_file, image_folder, 5)
    train_loader = torch.utils.data.DataLoader(ds, batch_size=1, shuffle=True)


if do == 5:
    image_transform = v2.Compose([v2.Grayscale()])
    read_bbox_csv_show_image()

if do == 6:
    with open(generated_data_dir() + "list_training_loss.pkl", "rb") as f1:
        list_training_loss = pickle.load(f1)
    with open(generated_data_dir() + "list_testing_loss.pkl", "rb") as f2:
        list_testing_loss = pickle.load(f2)

    epochs = range(1, len(list_training_loss) + 1)
    plt.plot(epochs, list_training_loss, "g", label="Training loss")
    plt.plot(epochs, list_testing_loss, "b", label="Testing loss")
    plt.xticks(range(1, len(list_training_loss) + 1))
    plt.title("Training and Validation loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.show()

if do == 61:
    prefix = ""
    if model == 2:
        prefix = "gru"
    elif model == 3:
        prefix = "lstm"
    elif model == 1:
        prefix = "rnn"

    with open(generated_data_dir() + "gru_list_testing_wer.pkl", "rb") as f3:
        gru_list_testing_wer = pickle.load(f3)
    with open(generated_data_dir() + "gru_list_testing_cer.pkl", "rb") as f4:
        gru_list_testing_cer = pickle.load(f4)
    with open(generated_data_dir() + "lstm_list_testing_wer.pkl", "rb") as f5:
        lstm_list_testing_wer = pickle.load(f5)
    with open(generated_data_dir() + "lstm_list_testing_cer.pkl", "rb") as f6:
        lstm_list_testing_cer = pickle.load(f6)
    with open(generated_data_dir() + "rnn_list_testing_wer.pkl", "rb") as f1:
        rnn_list_testing_wer = pickle.load(f1)
    with open(generated_data_dir() + "rnn_list_testing_cer.pkl", "rb") as f2:
        rnn_list_testing_cer = pickle.load(f2)
    epochs = range(1, len(lstm_list_testing_wer) + 1)
    plt.plot(epochs, gru_list_testing_wer, label="CRNN GRU testing wer", color="black")
    plt.plot(epochs, gru_list_testing_cer, label="CRNN GRU testing cer", color="blue")
    plt.plot(epochs, lstm_list_testing_wer, label="CRNN LSTM testing wer", color="red")
    plt.plot(
        epochs, lstm_list_testing_cer, label="CRNN LSTM testing cer", color="orange"
    )
    plt.plot(epochs, rnn_list_testing_wer, label="CRNN RNN testing wer", color="grey")
    plt.plot(epochs, rnn_list_testing_cer, label="CRNN RNN testing cer", color="green")
    plt.xticks(range(1, len(lstm_list_testing_wer) + 1))
    # plt.title('Testing wer/cer')
    plt.xlabel("Epochs")
    plt.ylabel("wer/cer")
    plt.legend()
    plt.show()

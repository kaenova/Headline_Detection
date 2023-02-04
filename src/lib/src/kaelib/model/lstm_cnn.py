# https://ieeexplore.ieee.org/document/8577620

import torch
import torch.nn as nn
from torchnlp.encoders.text import StaticTokenizerEncoder, pad_tensor

class StaticTokenizerEncoderWraper(StaticTokenizerEncoder):
    def prepare_text(self, text: str, max_seq_length: int):
        token = self.encode(text)
        if len(token) > max_seq_length:
            token = token[:max_seq_length]
        token = pad_tensor(token, max_seq_length)
        return token

class LSTM_CNN(nn.Module):
    def __init__(
        self,
        seq_length: int,
        text_vectorizer: StaticTokenizerEncoderWraper,
        device="cpu",
    ) -> None:
        super().__init__()

        # Config
        self.seq_length = seq_length
        self.device = device
        self.text_embed_size = 128

        # Layer
        self.text_vectorizer = text_vectorizer

        self.text_embeddings = nn.Embedding(
            text_vectorizer.vocab_size, self.text_embed_size, device=self.device
        )

        self.lstm_layer = nn.LSTM(
            input_size=self.text_embed_size,
            hidden_size=600,
            num_layers=2,
            batch_first=True,
            dropout=0.5,
        )

        self.conv_layer = nn.Sequential(
            nn.Conv1d(600, 64, 3),
            nn.MaxPool2d((64, 1)),
        )

        self.classification_head = nn.Sequential(
            nn.Flatten(), nn.Linear(254, 2)
        )

    def _prepare_text(self, x: "list[str]"):
        # Check input
        for i in x:
            if type(i) is not str:
                raise TypeError("x must be list of string")
        tokenized_text = [
            self.text_vectorizer.prepare_text(text, self.seq_length) for text in x
        ]
        tokenized_text = torch.stack(tokenized_text).int().to(self.device)
        return tokenized_text

    def forward(self, texts: "list[str]"):
        x_vec = self._prepare_text(texts)
        x = self.text_embeddings(x_vec)
        x: torch.Tensor = self.lstm_layer(x)[0]  # Get output of last hidden layer
        x_shape = x.shape
        x = x.reshape((x_shape[0], x_shape[2], x_shape[1]))
        x = self.conv_layer(x)
        x = self.classification_head(x)

        return x



if __name__ == "__main__":
    test_text = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum dapibus nibh in magna tempor, vel tristique enim gravida. Curabitur lectus eros, ornare nec convallis pulvinar, efficitur eget neque. Nulla facilisi. Aenean sagittis congue enim, sit amet vestibulum purus sodales eu. In hac habitasse platea dictumst. Morbi convallis, ligula et condimentum dictum, orci purus tristique enim, eu commodo ipsum quam ut ante. Praesent eu tortor sodales, eleifend libero ac, ornare tortor. Phasellus fermentum congue lorem, vitae posuere elit convallis nec. Vivamus ipsum ex, sodales id orci sed, tristique convallis dui. Praesent placerat consequat luctus. Curabitur imperdiet nibh non egestas pulvinar. Proin hendrerit imperdiet auctor. Vivamus ultricies mollis elit id porttitor.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras pharetra eros accumsan, consequat justo quis, venenatis ex. Aenean euismod interdum justo, sed accumsan tellus elementum et. Proin varius eget sem vitae lobortis. Fusce ex ex, suscipit a tellus nec, aliquet maximus leo. Sed vel risus risus. Suspendisse sollicitudin dictum quam sed sagittis. Curabitur fringilla tortor metus, vitae malesuada enim feugiat a. Aliquam scelerisque dictum elit, a tincidunt lorem mattis sed. Cras eu placerat elit, vitae iaculis mauris. Morbi et eros dui. Proin tincidunt, dui quis tristique imperdiet, nisi sapien eleifend elit, et consequat nisi lectus at lacus.

    Pellentesque elementum est id lobortis elementum. Nullam iaculis volutpat dolor, tincidunt sagittis ipsum fringilla vel. Proin tincidunt eu libero quis accumsan. Phasellus vitae erat viverra, condimentum orci luctus, finibus mi. Cras varius eleifend dolor, sed sollicitudin lectus rhoncus sodales. Phasellus suscipit porta metus. Phasellus bibendum elit et urna lacinia dictum.

    Proin erat purus, iaculis vel molestie eu, bibendum posuere felis. Quisque feugiat at eros ut fringilla. Pellentesque vel condimentum est. Proin rutrum varius orci, nec faucibus nibh vestibulum nec. Nunc vehicula sed urna id iaculis. Proin a arcu sit amet erat bibendum rhoncus non a arcu. Cras malesuada erat purus, et aliquam lacus sagittis pulvinar. Pellentesque rhoncus lectus tortor, eu luctus dolor eleifend eu. Suspendisse non condimentum massa. Pellentesque ultricies tellus a risus tempus vulputate. Fusce aliquet lobortis orci. Sed augue ante, aliquam ac enim at, vehicula mollis neque. Fusce porttitor mollis faucibus. Sed porta placerat erat, vel dapibus velit semper non. Maecenas luctus a ex non consequat. Nam eu efficitur eros.

    Phasellus id libero eu erat tempus accumsan. Donec semper tincidunt erat, non vehicula ipsum sollicitudin eget. Integer imperdiet vestibulum mauris tincidunt lacinia. Nunc tristique consequat turpis sed faucibus. Sed dapibus nisi vestibulum ligula egestas pharetra. Cras vitae elit eu diam hendrerit pulvinar vel tempus arcu. Praesent faucibus tortor eget rutrum tristique. Maecenas imperdiet gravida ex vel iaculis. Ut ullamcorper lectus tristique nisl hendrerit iaculis. Sed consectetur elementum tortor, vitae pharetra ex finibus non. Nam sollicitudin imperdiet sem, molestie euismod arcu tincidunt nec. Nulla eu consequat turpis, ut sagittis purus. Donec finibus vel diam vel
    """
    
    text_vectorizer = StaticTokenizerEncoderWraper(
        [test_text], tokenize=lambda s: s.split()
    )
    model = LSTM_CNN(seq_length=256, text_vectorizer=text_vectorizer)
    y = model.forward(["hello", "Phasellus id libero eu erat tempus accumsan"])
    print(model)

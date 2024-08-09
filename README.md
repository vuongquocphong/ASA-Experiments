# ASA-Experiments

This is the experimenting implementation of the topic Automatic Sentence Alignment for SinoNom and Vietnamese translation bitexts.

## How to run

### Init the environment

```{bash}
python -m venv myenv
```

### Activate the environment

- Linux/MacOS

```{bash}
source myenv/bin/activate
```

- Windows

```{bash}
.\myenv\Scripts\activate
```

### Length-based approach

```{python}
python -m approaches.length-based.file_name {source_file} {target_file} {gold_file} gacha
```

### Dictionary-based approach

```{python}
```

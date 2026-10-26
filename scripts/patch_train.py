from pathlib import Path

path = Path("backend/app/ai/train_image_model.py")
content = path.read_text(encoding="utf-8")

# 1. Normalize line endings
content = content.replace("\r\n", "\n")

# 2. Fix _transforms
transforms_old = """def _transforms():
    weights = None
    if use_pretrained:
        try:
            weights = ResNet18_Weights.DEFAULT
            model = models.resnet18(weights=weights)
        except Exception:
            model = models.resnet18(weights=None)
    else:
        model = models.resnet18(weights=None)

    normalize = weights.transforms()"""

transforms_new = """def _transforms():
    normalize = ResNet18_Weights.DEFAULT.transforms()"""

if transforms_old in content:
    content = content.replace(transforms_old, transforms_new)

# 3. Fix train signature and model creation
train_old = """    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, 2)
    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in model.fc.parameters():
        parameter.requires_grad = True

    optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3)"""

train_new = """    model.fc = nn.Linear(model.fc.in_features, 2)
    if weights is not None:
        for parameter in model.parameters():
            parameter.requires_grad = False
        for parameter in model.fc.parameters():
            parameter.requires_grad = True
        optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3)
    else:
        for parameter in model.parameters():
            parameter.requires_grad = True
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)"""

if train_old in content:
    content = content.replace(train_old, train_new)

# 4. Fix argument parser
parser_old = """    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()"""

parser_new = """    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--pretrained", action="store_true", default=False)
    args = parser.parse_args()"""

if parser_old in content:
    content = content.replace(parser_old, parser_new)

# 5. Fix train call
call_old = """    train(args.dataset, manifest, args.output, args.epochs, args.batch_size)"""
call_new = """    train(args.dataset, manifest, args.output, args.epochs, args.batch_size, use_pretrained=args.pretrained)"""

if call_old in content:
    content = content.replace(call_old, call_new)

path.write_text(content, encoding="utf-8")
print("SUCCESSFULLY PATCHED train_image_model.py")

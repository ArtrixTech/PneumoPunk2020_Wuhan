function LessManager() {
}

LessManager.prototype.allVars = {};
LessManager.prototype.init = () => {
    this.allVars = {};
}
LessManager.prototype.modifyVars = (vars) => {
    if (!window.less) throw Error = "Less was not loaded.";
    else {
        for (key in vars) this.allVars[key] = vars[key];
        less.modifyVars(this.allVars);
    }
}

LessManager.prototype.getVar = (inputKey) => {
    for (key in this.allVars)
        if (inputKey == key) return this.allVars[key];
    throw Error("No such var name '" + inputKey + "'")
}
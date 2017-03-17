(in-package :mt)

(setf *transfer-edge-limit* 5000)


(setf *transfer-maximum-rank* 2)

;;
;; the `language model' of dependency triples used to rank transfer outputs,
;; trained on the gold-standard ERG MRSs from the LOGON treebank
;;
(setf *transfer-tm*
 (namestring (lkb::lkb-pathname (lkb::parent-directory) "mrs.binlm")))

;;;(setf *transfer-tm*
;;;  (namestring (make-pathname 
;;;	       :directory (namestring
;;;			   (dir-append 
;;;			    (get-sources-dir "mt") '(:relative "mt")))
;;;	       :name "mrs.blm")))

;;
;; limit post-transfer SEM-I comparison to checking the validity of predicate
;; names and variable properties (but not role values and EP arity).
;;
(setf *semi-test* '(:predicates :properties))

;;; Mark the input to avoid loops

(defun preprocess (mrs)
  (let ((mrs-can (mrs::number-convert mrs))) ;;; add numbers together
    (loop
	for ep in (mrs:psoa-liszt mrs-can)
	do (setf (mrs:rel-pred ep) (format nil "~(ja:~a~)" (mrs:rel-pred ep))))
    mrs-can))
					;
					;
;;; We have various unknown predicates
;;;   from Japanese names we don't know: kyouko_2
;;;   from Japanese nouns we don't know: ja:_hayaguchi_n_1_rel
;;; clean them up a little in the post processing
;;;
;;; Possibly not so robust

(defun postprocess (mrs)
  (loop
      with carg = (mrs:vsym "CARG")
      for ep in (mrs:psoa-liszt mrs)
      when (equal (mrs:rel-pred ep) (mrs:vsym "named_rel"))
      do (loop
	     for role in (mrs:rel-flist ep)
	     for value = (mrs:fvpair-value role)
	     when (eq (mrs:fvpair-feature role) carg) 
	     do (setf (mrs:fvpair-value role)
		  ;; remove trailing _*
		  (clean-unknowns value))))
	 mrs)


(defun clean-unknowns (constant) 
  (first (cl-ppcre:split "_"  
			 ;; remove initial ja:_
			 (cl-ppcre:regex-replace "^(ja:)?_" constant ""))))



;; preprocess means that there are no interlingua predicates 
					
(defparameter *transfer-interlingua-predicates*
    '(lkb::person_rel lkb::compound_rel lkb::nominalization_rel))

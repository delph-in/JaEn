(in-package :mrs)

;;;
;;; these are general MRS variables, irrespective of the AVM encoding used in
;;; a particular grammar.
;;; 

(setf *rel-name-path* `(,(vsym "PRED") ))

(setf *rel-handel-path* (list (vsym "LBL")))

(setf *sc-arg-feature* (vsym "HARG"))

(setf *outscpd-feature* (vsym "LARG"))

(setf *bv-feature* (vsym "ARG0"))

(setf *scope-feat* (vsym "BODY"))

;;;
;;; _fix_me_
;;; for now, suppress LNK roles post-transfer this way; the right solution, i
;;; think, would be recording surface positions in a dedicated slot in the EP
;;; structure, analoguous to characterization information.    (30-jun-04; oe)
;;;
(setf *ignored-sem-features* 
  (list (vsym "LNK")))

(setf *top-semantics-type* (vsym "predsort"))

(setf *value-feats* 
  (list
   (vsym "CARG") (vsym "LNK")))

;;;
;;; the following are grammar-specific paths
;;;

(setf *sem-relation-suffix* "_rel")

(setf *ignored-extra-features* 
  (list 
   (vsym "SORT")))

(setf *initial-semantics-path* nil)

(setf *main-semantics-path* 
  (append *initial-semantics-path* (list (vsym "RELS"))))

(setf *construction-semantics-path* nil)

(setf *psoa-top-h-path* (list (vsym "LTOP")))

(setf *psoa-index-path* (list (vsym "INDEX")))

(setf *psoa-liszt-path* (list (vsym "RELS")))

(setf *psoa-rh-cons-path* (list (vsym "HCONS")))


;;;
;;; types for variable naming in output (copy from `.../src/mrs/mrsglobals.lsp'
;;; but here to remind us to adapt them, as appropriate).
;;;

(setf *event-type* (vsym "e"))
(setf *event_or_index-type* (vsym "i"))
(setf *handle-type* (vsym "h"))
(setf *ref-ind-type* (vsym "x"))

;;;
;;; interim solution for MRS `unfilling' until we construct a proper SEM-I
;;;
(setf %mrs-extras-filter%
  ;;
  ;; _fix_me_
  ;; even without the full SEMI, we should compute these.  (21-nov-03; oe)
  ;;
  (list
   (cons (mrs::vsym "NUM") (mrs::vsym "number"))
   (cons (mrs::vsym "PERS") (mrs::vsym "person"))
   (cons (mrs::vsym "NATGEND") (mrs::vsym "gender"))
   (cons (mrs::vsym "TENSE") (mrs::vsym "tense"))
   (cons (mrs::vsym "PROG") (mrs::vsym "luk"))
   (cons (mrs::vsym "PERF") (mrs::vsym "luk"))
   (cons (mrs::vsym "STATIVE") (mrs::vsym "luk"))
   (cons (mrs::vsym "BOUNDED") (mrs::vsym "luk"))
   (cons (mrs::vsym "E.TENSE") (mrs::vsym "tense"))
   (cons (mrs::vsym "E.TENSE") (mrs::vsym "basic_tense"))
   (cons (mrs::vsym "E.ASPECT.PROGR") (mrs::vsym "luk"))
   (cons (mrs::vsym "E.ASPECT.PERF") (mrs::vsym "luk"))
   (cons (mrs::vsym "E.MOOD") (mrs::vsym "mood"))
   (cons (mrs::vsym "PNG.GEN") (mrs::vsym "gender"))
   (cons (mrs::vsym "PNG.GEN") (mrs::vsym "real_gender"))
   (cons (mrs::vsym "PNG.PN") (mrs::vsym "pernum"))
   (cons (mrs::vsym "DIVISIBLE") (mrs::vsym "bool"))
   (cons (mrs::vsym "PRONTYPE") (mrs::vsym "prontype"))))

;;;
;;; for better debugging, print MRS structures readably, by default
;;;
#-:debug
(setf mrs::*mrs-raw-output-p* nil)
